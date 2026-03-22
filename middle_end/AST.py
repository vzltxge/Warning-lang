import ctypes
from abc import ABC
from typing import Any, final

from frontend.TOKENS import Token
from middle_end.POSITION import Pos
from types_.num_types import num_type

"""
Node class should be abstract
"""
# NOTE: These are the abstract classes


class Node(ABC):
  @final
  def __repr__(self) -> str:
    attribs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
    return f"{self.__class__.__name__}({attribs})\n"


class Expr(Node): ...


class Stmt(Node): ...


# NOTE: NodeTypes


class Number(Expr):
  def __init__(self, token: Token, type_: num_type | None) -> None:
    self.token = token
    self.pos_start: Pos = self.token.pos_start
    self.pos_end: Pos = self.token.pos_end
    self.type_ = type_
    self.checked_size: bool = False
    self.casted: bool = False
    if not type_:
      # NOTE: Add auto type guessing so the number uses the least amount of memory possible.
      if type(token.value) is not float:
        self.type_ = ctypes.c_int64
      else:
        self.type_ = ctypes.c_double
    self.is_typed: bool = False  # NOTE: True when number is assigned to variable

  def __eq__(self, other) -> bool:
    return (
      isinstance(other, Number)
      and self.token == other.token
      and self.type_ == other.type_
    )


class VarAccess(Expr):
  def __init__(self, var_name_token: Token) -> None:
    self.var_name_token = var_name_token

    # Just learn this was a thing today, Date: 7th Jan 2026
    self.pos_start: Pos
    self.pos_end: Pos
    self.pos_start, self.pos_end = (
      self.var_name_token.pos_start,
      self.var_name_token.pos_end,
    )
    self.type_ = None
    self.is_const: bool = False


class VarAssign(Stmt):
  def __init__(
    self, var_name_tok: Token, value_node, type_: Any, is_value_const: bool = False
  ) -> None:
    self.var_name_token = var_name_tok
    self.value_node = value_node
    self.value_node.is_typed = True
    self.type_ = type_
    self.pos_start: Pos
    self.pos_end: Pos
    self.pos_start, self.pos_end = (
      self.var_name_token.pos_start,
      self.var_name_token.pos_end,
    )
    self.is_value_const: bool = is_value_const


# NOTE: This is for ! and - unary operators
class UnaryOp(Expr):
  def __init__(self, op_tok: Token, node: Number | VarAccess) -> None:
    self.op_tok = op_tok
    self.node = node
    self.pos_start = self.op_tok.pos_start
    self.pos_end = self.node.pos_end


class BinOp(Expr):
  def __init__(self, left_node, op_token: Token, right_node) -> None:
    self.left_node = left_node
    self.right_node = right_node
    self.op_token: Token = op_token
    self.pos_start: Pos = self.left_node.pos_start
    self.pos_end: Pos = self.right_node.pos_end


class Increment(Expr):
  def __init__(self, value: VarAccess, postfix: bool = False) -> None:
    self.value = value
    self.postfix = postfix
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.value.pos_end


class IncrementBy(Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end


class Decrement(Expr):
  def __init__(self, value: VarAccess, postfix: bool = False) -> None:
    self.value = value
    self.postfix = postfix
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.value.pos_end


class DecrementBy(Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end


class MultiplyBy(Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end


class DivideBy(Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end


# NOTE: This will be and expression by default


class IfExpr(Expr):
  def __init__(self, cases: list, else_case) -> None:
    self.cases: list = cases
    self.else_case = else_case
    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.cases[len(self.cases) - 1][0]).pos_end


class WhileStmt(Stmt):
  def __init__(self, condition, block: list):
    self.condition = condition
    self.block = block
    self.pos_start: Pos = self.condition.pos_start
    if not block:
      self.pos_end: Pos = self.condition.pos_end
    else:
      self.pos_end: Pos = self.block[-1].pos_end


class RangeNode(Node):
  def __init__(self, start: int, end: int, step=None) -> None:
    self.start = start
    self.end = end
    self.step = step


class ForExpr(Expr):
  def __init__(self, var_name, range: RangeNode, block: list):
    self.var_name = var_name
    self.range = range
    self.block = block
    self.pos_start = self.var_name.pos_start
    self.pos_end = self.block[-1].pos_end

class FuncDef(Stmt):
  def __init__(self, var_name_tok: str, arg_name_toks: list[Node], body_node: list[Node]):
    ...