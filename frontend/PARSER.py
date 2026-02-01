# Imports
from typing import Any, Self

from frontend.TOKENS import TT, Token
from middle_end.AST import (
  BinOp, Decrement,
  DecrementBy, ForExpr,
  IfExpr, Increment,
  IncrementBy, Number,
  RangeNode, UnaryOp,
  VarAccess, VarAssign,
  WhileStmt,
)
from middle_end.ERRORS import InvalidSyntaxError, MissingSemicolonError
from middle_end.POSITION import Pos
from runtime.typemap import inverse_type_map


class ParseResult:
  def __init__(self) -> None:
    self.error = None
    self.node = None
    self.advance_count: int = 0

  def register(self, res):
    self.advance_count += res.advance_count
    if res.error:
      self.error = res.error
    return res.node

  def register_advancement(self) -> None:
    self.advance_count += 1

  def success(self, node) -> Self:
    self.node = node
    return self

  def failure(self, error) -> Self:
    if not self.error or self.advance_count == 0:  # NOTE: haven't advanced since
      self.error = error
    return self


class Parser:
  def __init__(self, tokens: list[Token]) -> None:
    self.tokens = tokens
    self.token_index = -1
    self.advance()
    self.prev_token: Token

  def expect(self, type_, value=None) -> bool:
    if type(type_) is tuple:
      return self.current_token.type in type_
    return self.current_token.type == type_ and self.current_token.value == value if value else self.current_token.type == type_
  def advance(self) -> Token:
    self.token_index += 1
    if self.token_index < len(self.tokens):
      self.current_token: Token = self.tokens[self.token_index]
      self.prev_token: Token = self.tokens[self.token_index - 1] if self.token_index > 0 else None
    return self.current_token
  def consume(self, res: ParseResult):
    self.advance()
    res.register_advancement()
  # Factor is int, float, var, increment, decrement
  def factor(self) -> ParseResult:
    tok: Token = self.current_token
    res: ParseResult = ParseResult()
    # This is for prefix increment/decrement
    if self.current_token.type in (TT.INCREMENT, TT.DECREMENT):
      self.advance()
      res.register_advancement()
      value = res.register(self.factor())
      if res.error:
        return res
      return res.success(Increment(value) if tok.type == TT.INCREMENT else Decrement(value))
    if tok.type in (TT.PLUS, TT.MINUS):
      self.consume(res)
      factor = res.register(self.factor())
      if res.error:
        return res
      return res.success(UnaryOp(tok, factor))

    elif tok.type in (TT.INT, TT.FLOAT):
      self.consume(res)
      # This is for postfix increment/decrement

      return res.success(Number(tok, type_=None))
    elif tok.type == TT.IDENT:
      self.consume(res)
      node = VarAccess(tok)
      if self.current_token.type in (TT.INCREMENT, TT.DECREMENT):
        op_tok = self.current_token
        self.consume(res)
        return res.success(Increment(node, True) if op_tok.type == TT.INCREMENT else Decrement(node, True))
      return res.success(VarAccess(tok))
    elif self.expect(TT.LPAREN):
      self.consume(res)
      expr = res.register(self.expr())
      if res.error:
        return res
      if self.expect(TT.RPAREN):
        self.consume(res)
        return res.success(expr)

      else:
        return res.failure(
            InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected ')'",
            ))
    return res.failure(
        InvalidSyntaxError(tok.pos_start, tok.pos_end,
                          "Expected int, float or identifier"))

  def parse(self):
    res = self.stmts()
    if not res.error and not self.expect(TT.EOF):
      return res.failure(
          InvalidSyntaxError(
              self.prev_token.pos_start,
              self.current_token.pos_end,
              "Expected `+`, `-`, `*` or `/`",
          ))

    return res

  def stmts(self):
    res = ParseResult()
    statements = []
    while not self.expect(TT.EOF) and not self.expect(TT.RBRACE):
      stmt = res.register(self.stmt())
      if res.error:
        return res
      if self.expect(TT.SEMI):
        self.consume(res) #Consumes semicolon 👍⚠️
      else:
        return res.failure(
            MissingSemicolonError(
                self.prev_token.pos_start,
                self.prev_token.pos_end,
                "Expected `;`, next time add it!",
            ))
      statements.append(stmt)
    return res.success(statements)

  def power(self):
    res = ParseResult()
    left = res.register(self.factor())
    if res.error:
      return res

    # Check for None and cast to help type checker
    if left is None:
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Invalid left operand in power expression",
          ))

    if self.expect(TT.POW):
      op_tok = self.current_token
      self.consume(res)
      right = res.register(self.power())  # 🔥 right-associative
      if res.error:
        return res

      # Check for None and cast to help type checker
      if right is None:
        return res.failure(
            InvalidSyntaxError(
                op_tok.pos_start,
                op_tok.pos_end,
                "Invalid right operand in power expression",
            ))
      return res.success(BinOp(left, op_tok, right))
    return res.success(left)

  # Term is Mulitply or Divide
  def term(self):
    return self.bin_op(self.power, (TT.MUL, TT.DIV))

  # Function to prevent duplication of code
  def bin_op(self, func, tokens: tuple):
    res = ParseResult()
    left = res.register(func())
    if res.error:
      return res

    # Check for None and cast to help type checker
    if left is None:
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Invalid left operand",
          ))
    while self.current_token.type in tokens:
      op_tok = self.current_token
      self.consume(res)
      right = res.register(func())
      if res.error:
        return res

      # Check for None and cast to help type checker
      if right is None:
        return res.failure(
            InvalidSyntaxError(op_tok.pos_start, op_tok.pos_end,
                               "Invalid right operand"))

      left = BinOp(left, op_tok, right)
    return res.success(left)
  # NOTE: Handles increment
  # Handles incremnt by statements
  def incr_by(self) -> ParseResult:
     res: ParseResult = ParseResult()
     self.consume(res)
     variable = res.register(self.factor())
     if res.error:
       return res

     if not self.expect(type_=TT.KEYWORD, value="by"):
       return res.failure(
           InvalidSyntaxError(
               self.current_token.pos_start,
               self.current_token.pos_end,
               "Expected `by` keyword",
           ))

     self.consume(res)

     amount = res.register(self.factor())
     if res.error:
       return res
     return res.success(IncrementBy(variable, amount=amount))

  # NOTE: handles decrement by statements
  def decr_by(self) -> ParseResult:
     res: ParseResult = ParseResult()
     self.advance()
     res.register_advancement()
     variable = res.register(self.factor())
     if res.error:
       return res

     if not self.expect(type_=TT.KEYWORD, value="by"):
       return res.failure(
           InvalidSyntaxError(
               self.current_token.pos_start,
               self.current_token.pos_end,
               "Expected `by` keyword",
           ))
     res.register_advancement()
     self.advance()

     amount = res.register(self.factor())
     if res.error:
       return res
     return res.success(DecrementBy(variable, amount=amount))

  def while_stmt(self):
    res: ParseResult = ParseResult()
    pos_start: Pos = self.current_token.pos_start.copy()
    self.advance()
    res.register_advancement()

    condition = res.register(self.expr())
    if not self.expect(TT.LBRACE):
      return res.failure(InvalidSyntaxError(
        details="Bro you are missing a `{`!",
        pos_start=pos_start, pos_end=self.current_token.pos_end
      ))

    self.advance()
    res.register_advancement()
    block = res.register(self.stmts())
    if res.error:
      return res

    if not self.expect(TT.RBRACE):
      return res.failure(InvalidSyntaxError(
        details="Bro you are missing a `}`!",
        pos_start=pos_start, pos_end=self.current_token.pos_end
      ))

    self.advance()
    res.register_advancement()

    return res.success(WhileStmt(condition=condition, block=block))

  def for_expr(self):
    res: ParseResult = ParseResult()
    pos_start = self.current_token.pos_start.copy()
    self.advance()

    # NOTE: This checks for an identifier after the for keyword
    if not self.expect(TT.IDENT):
      return res.failure(InvalidSyntaxError(
        details=f"Expected a variable/indentifier not {self.current_token}",
        pos_start=pos_start, pos_end=self.current_token.pos_end
      ))

    var_name: Token = self.current_token
    self.advance()
    res.register_advancement()

    #NOTE: This check for the in keyword
    if not self.current_token.matches(TT.KEYWORD, "in"):
      return res.failure(InvalidSyntaxError(
        details=f"Expected `in` keyword not {self.current_token}",
        pos_start=pos_start, pos_end=self.current_token.pos_end
      ))

    self.advance()
    res.register_advancement()
    range_node = res.register(self.range_expr())
    if res.error:
      return res

    # NOTE: This checks for a step keyword
    if self.current_token.matches(TT.KEYWORD, "step"):
        res.register_advancement()
        self.advance()
        range_node.step = res.register(self.arith_expr())
        if res.error:
          return res
    if not self.expect(TT.LBRACE):
      return res.failure(
        InvalidSyntaxError(pos_start=self.current_token.pos_start, pos_end=self.current_token.pos_end, details="Expected `{`")
      )
    res.register_advancement()
    self.advance()

    block = res.register(self.stmts())
    if res.error:
      return res
    if not self.expect(TT.RBRACE):
        return res.failure(InvalidSyntaxError(
            details="Expected '}' not " + str(self.current_token.value),
            pos_start=self.current_token.pos_start,
            pos_end=self.current_token.pos_end
        ))
    res.register_advancement()
    self.advance()
    return res.success(ForExpr(var_name, range_node, block=block))

  def range_expr(self):
    res = ParseResult()
    left = res.register(self.arith_expr())
    if res.error:
      return res

    if self.current_token.type == TT.RANGE:
      res.register_advancement()
      self.advance()

      right = res.register(self.arith_expr())
      if res.error:
        return res

      return res.success(RangeNode(left, right))
    return res.success(left)
  def make_var(self, res: ParseResult, type_):
    value_type = self.current_token
    is_const: bool = False
    # NOTE: Make this a list when you add for float types
    res.register_advancement()
    self.advance()  # eat 'i64, i32 etc.'
    
    if self.expect(type_=TT.KEYWORD, value="const"):
      is_const = True
      self.consume(res)
      
    if not self.expect(TT.IDENT):
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Expected identifier",
          ))

    var_name = self.current_token
    res.register_advancement()
    self.advance()  # eat identifier
    if self.current_token.type != TT.EQ:
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Expected '=' not " + str(self.current_token.value),
          ))
    res.register_advancement()
    self.advance()
    value: Any = res.register(self.expr())
    is_unary: bool = isinstance(value, UnaryOp)
    # ? Use a match case for this
    is_value_number: bool = isinstance(value, Number)
    if is_value_number or is_unary:
      type_ = inverse_type_map.get(value_type.value)
      if is_unary:
        value.node.type_ = type_
      value.type_ = type_
    if res.error:
      return res

    return res.success(VarAssign(var_name, value, type_, is_value_const=is_const))

  def stmt(self) -> ParseResult:
    res: ParseResult = ParseResult()
    if self.current_token.matches(TT.KEYWORD,
                                  "if") or self.current_token.matches(
                                      TT.KEYWORD, "vibecheck"):
      if_expr = res.register(self.if_expr())
      if res.error:
        return res
      return res.success(if_expr)

    elif self.current_token.matches(TT.KEYWORD, "for") or self.current_token.matches(TT.KEYWORD, "loopsy"):
      for_expr = res.register(self.for_expr())
      if res.error:
        return res
      return res.success(for_expr)
    elif self.current_token.matches(TT.KEYWORD, "incr"):
          incr_stmt = res.register(self.incr_by())
          if res.error:
            return res
          return res.success(incr_stmt)
    elif self.current_token.matches(TT.KEYWORD, "decr"):
      decr_stmt = res.register(self.decr_by())
      if res.error:
        return res
      return res.success(decr_stmt)
    elif self.current_token.matches(TT.KEYWORD, "while") or self.current_token.matches(TT.KEYWORD, "rickroll"):
      while_stmt = res.register(self.while_stmt())
      if res.error:
        return res
      return res.success(while_stmt)

    if self.current_token.type == TT.KEYWORD and self.current_token.value in (
        "i64", "i32", "i16","i8",
        "u64", "u32", "u16","u8",
        "f32", "f64",
    ):
      node = res.register(
          self.make_var(res=res, type_=self.current_token.value))
      return res.success(node)
    return self.expr()

  # Expression
  def expr(self) -> ParseResult:
    res: ParseResult = ParseResult()
    node = res.register(self.bin_op(self.comp_expr, (TT.AND, TT.OR)))
    if res.error:
      return res
    return res.success(node)

  def arith_expr(self):
    return self.bin_op(self.term, (TT.PLUS, TT.MINUS))

  def if_expr(self):
    res = ParseResult()
    cases = []
    else_case = None
    res.register_advancement()
    self.advance()
    condition = res.register(self.expr())
    # NOTE: If code fails advance and register advance method here
    if res.error:
      return res

    if not self.expect(TT.LBRACE):
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Expected '{', Next time add it or else",
          ))

    res.register_advancement()
    self.advance()
    body = res.register(self.stmts())
    if res.error:
      return res
    if self.current_token.type != TT.RBRACE:
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Expected '}', Next time add it or else",
          ))
    res.register_advancement()
    self.advance()

    cases.append((condition, body))

    # NOTE: HANDLES MULTIPLE ELIF CASES
    while self.current_token.matches(
            TT.KEYWORD, "elif") or self.current_token.matches(TT.KEYWORD, "also"):
      res.register_advancement()
      self.advance()
      condition = res.register(self.comp_expr())
      if res.error:
        return res

      if self.current_token.type != TT.LBRACE:
        return res.failure(
            InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected '{', Next time add it or else",
            ))
      self.advance()
      res.register_advancement()

      body = res.register(self.stmts())
      if res.error:
        return res
      if self.current_token.type != TT.RBRACE:
        return res.failure(
            InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected '}', Next time add it or else",
            ))
      self.advance()
      res.register_advancement()

      cases.append((condition, body))

    # NOTE: HANDLES ELSE CASE
    if (self.current_token.matches(TT.KEYWORD, "else")
        or self.current_token.matches(TT.KEYWORD, "idk")):
      res.register_advancement()
      self.advance()
      if self.current_token.type != TT.LBRACE:
        return res.failure(
            InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected '{'",
            ))
      self.advance()
      res.register_advancement()
      else_case = res.register(self.stmts())
      if res.error:
        return res

      if self.current_token.type != TT.RBRACE:
        return res.failure(
            InvalidSyntaxError(
                self.current_token.pos_start,
                self.current_token.pos_end,
                "Expected '}'",
            ))
      self.advance()
    return res.success(IfExpr(cases, else_case))

  def comp_expr(self):
    res = ParseResult()
    if self.expect(TT.NOT):
      op_tok = self.current_token
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error:
        return res
      return res.success(UnaryOp(op_tok, node))
    node = res.register(
        self.bin_op(
            self.range_expr,
            (TT.DOUBLE_EQ, TT.GT, TT.G_EQ, TT.LT, TT.L_EQ, TT.NOT_EQ),
        ))
    if res.error:
      return res.failure(
          InvalidSyntaxError(
              self.current_token.pos_start,
              self.current_token.pos_end,
              "Expected int | float, identifier, `+`, `-`, `!` or `(` ",
          ))
    return res.success(node)
