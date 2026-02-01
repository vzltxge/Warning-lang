from middle_end.POSITION import Pos
from frontend.TOKENS import Token
from abc import ABC
import ctypes
from typing import Any, TypeAlias, final
num_type: TypeAlias = (ctypes.c_int64
                      | ctypes.c_int32
                      | ctypes.c_int16
                      | ctypes.c_float
                      | ctypes.c_double
                      | ctypes.c_uint8
                      | ctypes.c_uint16
                      | ctypes.c_uint32
                      | ctypes.c_uint64
                      | ctypes.c_double
                      | ctypes.c_float
                       )

"""
Node class should be abstract
"""
# NOTE: These are the abstract classes
class Node(ABC):
  @final
  def __repr__(self):
    attribs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
    return f"{self.__class__.__name__}({attribs})\n"
class Expr(ABC):
  def __init__(self) -> None:
    ...
class Stmt(ABC):
  def __init__(self) -> None:
    ...


# NOTE: Nodes
class Number(Node, Expr):
  def __init__(self, token: Token, type_: num_type | None) -> None:
    self.token = token
    self.pos_start: Pos = self.token.pos_start
    self.pos_end: Pos = self.token.pos_end
    self.type_ = type_
    self.checked_size: bool = False
    self.casted: bool = False
    self.is_typed: bool = False # used for when number is assigned to a variable
    if not type_:
      self.type_ = ctypes.c_int64
  def __eq__(self, other) -> bool:
    return isinstance(other, Number) and self.token == other.token and self.type_ == other.type_


class VarAccess(Node, Expr):
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

# Keyword for assigning is make but the name should still be var assign
class VarAssign(Node, Stmt):
  def __init__(self, var_name_tok: Token, value_node, type_: Any, is_value_const: bool = False) -> None:
    self.var_name_token = var_name_tok
    self.value_node = value_node
    self.type_ = type_
    self.pos_start: Pos
    self.pos_end: Pos
    self.pos_start, self.pos_end = (
        self.var_name_token.pos_start,
        self.var_name_token.pos_end,
    )
    self.is_value_const: bool = is_value_const

class UnaryOp(Node, Expr):
  def __init__(self, op_tok: Token, node) -> None:
    self.op_tok = op_tok
    self.node = node
    self.pos_start = self.op_tok.pos_start
    self.pos_end = self.node.pos_end
    
class BinOp(Node, Expr):
  def __init__(self, left_node, op_token: Token,
               right_node) -> None:
    self.left_node: Node = left_node
    self.right_node: Node = right_node
    self.op_token: Token = op_token
    self.pos_start: Pos = self.left_node.pos_start
    self.pos_end: Pos = self.right_node.pos_end
    
    
class Increment(Node, Expr):
  def __init__(self, value: VarAccess, postfix: bool=False) -> None:
    self.value = value
    self.postfix = postfix
    self.pos_start = self.value.pos_start
    self.pos_end = self.value.pos_end

class IncrementBy(Node, Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end


class Decrement(Node, Expr):
  def __init__(self, value: VarAccess, postfix: bool=False) -> None:
    self.value = value
    self.postfix = postfix
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.value.pos_end


class DecrementBy(Node, Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end

class MultiplyBy(Node, Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end

class DivideBy(Node, Expr):
  def __init__(self, value: VarAccess, amount: Number) -> None:
    self.value = value
    self.amount = amount
    self.pos_start: Pos = self.value.pos_start
    self.pos_end: Pos = self.amount.pos_end

# NOTE: This will be and expression by default
class IfExpr(Node, Expr):
  def __init__(self, cases: list, else_case) -> None:
    self.cases: list = cases
    self.else_case = else_case
    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.cases[len(self.cases) - 1][0]).pos_end

class WhileStmt(Node, Stmt):
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

class ForExpr(Node, Expr):
  def __init__(self, var_name, range: RangeNode, block: list):
    self.var_name = var_name
    self.range = range
    self.block = block
    self.pos_start = self.var_name.pos_start
    self.pos_end = self.block[-1].pos_end
    