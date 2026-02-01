from enum import Enum
from typing import Any
from middle_end.POSITION import Pos


class TT(Enum):
  # Types
  INT = "INT"
  FLOAT = "FLOAT"

  # Operators
  MINUS = "MINUS"
  MUL = "MUL"
  PLUS = "PLUS"
  DIV = "DIV"
  POW = "POW"
  EQ = "EQ"
  INCREMENT = "INCREMENT" # ++
  INCRBY = "INCRBY" # +=
  DECREMENT = "DECREMENT" # --
  DECRBY = "DECRBY" # -=

  # Braces or brackets
  LPAREN = "LPAREN"
  RPAREN = "RPAREN"
  LBRACE = "LBRACE"  # {
  RBRACE = "RBRACE"  # }

  # Special
  IDENT = "IDENT"
  KEYWORD = "KEYWORD"
  SEMI = "SEMI"
  EOF = "EOF"
  RANGE = "RANGE" # ...
  # Comparision Operators
  DOUBLE_EQ = "DOUBLE_EQ"  # ==
  NOT_EQ = "NOT_EQ"  # !=
  L_EQ = "L_EQ"  # <=
  G_EQ = "G_EQ"  # >=
  GT = "GT"  # >
  LT = "LT"  # <
  AND = "AND"  # &
  OR = "OR"  # |
  NOT = "NOT"  # !


class Token:

  def __init__(
      self,
      type_: TT,
      value: Any = None,
      pos_start: Pos | None = None,
      pos_end: Pos | None = None,
  ) -> None:
    self.type = type_
    self.value = value
    if pos_start:
      self.pos_start: Pos = pos_start
      self.pos_end: Pos = pos_start.copy()
      self.pos_end.advance()
    if pos_end:
      self.pos_end = pos_end

  def __str__(self) -> str:
    if not self.value:
      return f"{self.type.value}"
    return f"{self.type.value}:{self.value}"

  def matches(self, type_: TT, value: Any) -> bool:
    return self.type == type_ and self.value == value

  def __repr__(self) -> str:
    return str(self)

  def format(self) -> str:
    if not self.value:
      return f"{self.type.value}"
    return f"{self.type.value}:{self.value}"