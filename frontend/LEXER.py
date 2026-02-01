# NOTE: Started project on 4th January 2025.
# NOTE: This is the thing that caused me, pain and suffering all my life.
from frontend.TOKENS import Token, TT
from middle_end.ERRORS import ExpectedCharError, IllegalCharError, Error
from middle_end.POSITION import Pos
from typing import Any
import string

# NOTE: Lexing
class Lexer:
  def __init__(self, fn: str, code: str) -> None:
    self.code = code
    self.fn = fn
    self.pos: Pos = Pos(index=-1,
                        line_num=0,
                        col_num=-1,
                        fn=self.fn,
                        ftxt=code)
    self.current_char: str | None = None
    self.advance()
    self.__operators: dict[str, TT] = {
        "/": TT.DIV,
        "*": TT.MUL,
        "^": TT.POW,
        # NOTE: The plus and minus operators will be handles seperately 
    }
    self.KEYWORDS: list[str] = [
        "i64", "i32", "i16","i8",        # Signed Integer Types
        "u64", "u32", "u16","u8",       # Unsigned Integer Types
        "f32", "f64",                   # Float Types 
        "if", "else", "elif",           # Conditionals
        "for", "while", "step", "in",   # Loops
        "decr", "incr", "mult", "div", "by", # Modifying variable by an amount
        "const",  # State of a variable
    ]
    self.ALTKEYWORDS: list[str] = ["vibecheck", "also", "idk", "rickroll", "loopsy"]
    self.__digits: str = "0123456789"
    self.__letters: str = string.ascii_letters
    self.__letters_digits: str = self.__digits + self.__letters

  # NOTE: Advance method
  def advance(self) -> None:
    self.pos.advance(self.current_char)
    self.current_char = (self.code[self.pos.index]
                         if self.pos.index < len(self.code) else None)
  # NOTE: Responsible for handling numbers
  def get_number(self, tokens) -> Token:
    num_str: str = ""
    dot_count: int = 0
    pos_start: Pos = self.pos.copy()
    while self.current_char and self.current_char in self.__digits or (self.current_char == '.' and self.peek() and self.peek().isdigit()):
      if self.current_char == ".":
        dot_count += 1
        self.advance()
      if dot_count > 1:
        break
      else:
        num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return Token(
          type_=TT.INT,
          value=int(num_str),
          pos_start=pos_start,
          pos_end=self.pos.copy(),
      )
    return Token(
        type_=TT.FLOAT,
        value=float(num_str),
        pos_start=pos_start,
        pos_end=self.pos.copy(),
    )
  def peek(self, distance: int=1):
    idx: int = self.pos.index + distance
    if idx < len(self.code):
      return self.code[idx]
    return None
  # NOTE: Expects a character and if found returns a token with a given type, value, pos start and pos_end
  def expect(self,
             char: str,
             type_: TT,
             pos_start: Pos,
             pos_end: Pos,
             value: Any = None) -> Token | None:
    if self.current_char == char:
      return Token(type_=type_,
                   value=value,
                   pos_start=pos_start,
                   pos_end=pos_end)

  # * Handles identifiers
  def get_identifier(self):
    id_str: str = ""
    pos_start = self.pos.copy()

    while self.current_char and self.current_char in self.__letters_digits + "_":
      id_str += self.current_char
      self.advance()
    if id_str in self.KEYWORDS + self.ALTKEYWORDS:
      token_type = TT.KEYWORD
    else:
      token_type = TT.IDENT
    return Token(token_type, id_str, pos_start, self.pos)

  # * This function handle not equals (!=)
  def make_not_eq(self) -> tuple[Token, None]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "=":
      self.advance()
      return Token(type_=TT.NOT_EQ, pos_start=pos_start,
                   pos_end=self.pos), None
    return Token(type_=TT.NOT, pos_start=pos_start, pos_end=self.pos), None

  # * This function handles eq and double eq {==, =}
  def make_eq(self) -> tuple[Token, None]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "=":
      self.advance()
      return (
          Token(type_=TT.DOUBLE_EQ, pos_start=pos_start, pos_end=self.pos),
          None,
      )
    return Token(type_=TT.EQ, pos_start=pos_start, pos_end=self.pos), None

  # * Function handles < and <=
  def make_less_than(self) -> tuple[Token, None]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "=":
      self.advance()
      return Token(type_=TT.L_EQ, pos_start=pos_start, pos_end=self.pos), None
    return Token(type_=TT.LT, pos_start=pos_start, pos_end=self.pos), None

  # * Function that handles > and >=
  def make_greater_than(self) -> tuple[Token, None]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "=":
      self.advance()
      return Token(type_=TT.G_EQ, pos_start=pos_start, pos_end=self.pos), None
    return Token(type_=TT.GT, pos_start=pos_start, pos_end=self.pos), None

  # * Function that handles &&
  def make_and(self) -> tuple[Token, None] | tuple[list, Error]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "&":
      self.advance()
      return Token(type_=TT.AND, pos_start=pos_start, pos_end=self.pos), None
    return [], ExpectedCharError(
        pos_start,
        self.pos,
        details="Expected another `&`, use `&&` next time!")

  # * Function that handles ||
  def make_or(self) -> tuple[Token, None] | tuple[list, Error]:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "|":
      self.advance()
      return Token(type_=TT.OR, pos_start=pos_start, pos_end=self.pos), None
    return [], ExpectedCharError(
        pos_start,
        self.pos,
        details="Expected another `|`, use `||` next time!\nOr else...",
    )

  # NOTE: This handles increment and increment by (++, +=)
  def make_increment(self) -> Token:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "+":
      self.advance()
      return Token(type_=TT.INCREMENT, pos_start=pos_start, pos_end=self.pos)
    elif self.current_char == "=":
      self.advance()
      return Token(type_=TT.INCRBY, pos_start=pos_start, pos_end=self.pos)
    return Token(type_=TT.PLUS, pos_start=pos_start, pos_end=self.pos)


  # NOTE: This handles decrement and decrement by (--, -=)
  def make_decrement(self) -> Token:
    pos_start: Pos = self.pos.copy()
    self.advance()
    if self.current_char == "-":
      self.advance()
      return Token(type_=TT.DECREMENT, pos_start=pos_start, pos_end=self.pos)
    elif self.current_char == "=":
      self.advance()
      return Token(type_=TT.DECRBY, pos_start=pos_start, pos_end=self.pos)
    return Token(type_=TT.MINUS, pos_start=pos_start, pos_end=self.pos)
  # * Gets tokens and returns the tokens
  def get_tokens(self) -> tuple[list[Token], list[Error]]:
    tokens: list[Token] = []
    errors: list[Error] = []
    # NOTE: Use a match-case statement later ...
    while self.current_char:
      # print(f"The position is {self.pos} and the current char is {self.current_char}")
      # TODO: Handle whitespace and newlines properly so errors can show correct line numbers
      if self.current_char == "\t":
        self.advance()
        self.advance()
      elif self.current_char == " ":
        self.advance()
      elif self.current_char == "\n":
        self.advance()
      elif self.current_char == "+":
        token = self.make_increment()
        tokens.append(token)
      elif self.current_char == "-":
        token = self.make_decrement()
        tokens.append(token)
      elif self.current_char == ";":
        tokens.append(
            Token(type_=TT.SEMI, pos_start=self.pos, pos_end=self.pos))
        self.advance()
      elif self.current_char == ".":
        pos_start = self.pos.copy()
        if self.peek() == '.' and self.peek(2) == '.':
          tokens.append(Token(type_=TT.RANGE, pos_start=pos_start, pos_end=self.pos))
        self.advance()
      elif self.current_char in self.__letters:
        tokens.append(self.get_identifier())

      elif self.current_char in self.__digits:
        tokens.append(self.get_number(tokens))

      elif self.current_char == "(":
        tokens.append(
            Token(type_=TT.LPAREN, value=self.current_char,
                  pos_start=self.pos))
        self.advance()
      elif self.current_char == "{":
        tokens.append(
            Token(type_=TT.LBRACE, value=self.current_char,
                  pos_start=self.pos))
        self.advance()
      elif self.current_char == "}":
        tokens.append(
            Token(type_=TT.RBRACE, value=self.current_char,
                  pos_start=self.pos))
        self.advance()
      elif self.current_char == ")":
        tokens.append(
            Token(type_=TT.RPAREN, value=self.current_char,
                  pos_start=self.pos))
        self.advance()

      elif self.current_char == "!":
        token, error = self.make_not_eq()
        if error:
          return [], [error]
        tokens.append(token)

      elif self.current_char == "=":
        token, error = self.make_eq()
        if error:
          return [], [error]
        tokens.append(token)

      elif self.current_char == "<":
        token, error = self.make_less_than()
        if error:
          return [], [error]
        tokens.append(token)

      elif self.current_char == ">":
        token, error = self.make_greater_than()
        if error:
          return [], [error]
        tokens.append(token)

      elif self.current_char == "&":
        result = self.make_and()
        if len(result) == 2 and isinstance(result[1], Error):
          return [], [result[1]]
        token, error = result
        if isinstance(token, Token):
          tokens.append(token)

      elif self.current_char == "|":
        result = self.make_or()
        if len(result) == 2 and isinstance(result[1], Error):
          return [], [result[1]]
        token, error = result
        if isinstance(token, Token):
          tokens.append(token)

      # NOTE: Handles +, -, /, * and ^
      elif self.current_char in self.__operators:
        tokens.append(
            Token(self.__operators[self.current_char], pos_start=self.pos))
        self.advance()

      else:
        char = self.current_char
        pos_start: Pos = self.pos.copy()
        print(f"The current char is {self.current_char}")
        print(repr(self.current_char))
        self.advance()
        errors.append(
            IllegalCharError(pos_start=pos_start,
                             pos_end=self.pos,
                             details=char))
        break
    tokens.append(Token(type_=TT.EOF, pos_start=self.pos))
    if errors:
      return [], errors
    return tokens, errors
