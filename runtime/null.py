from typing import Literal, Self
from middle_end.POSITION import Pos
from runtime.context import Context


class Null:
  def __init__(self) -> None:
    self.set_pos()
    self.set_context()
    self.value = None

  def __str__(self) -> str:
    return "null"

  def copy(self) -> Self:
    return self

  def set_pos(self, pos_start: Pos | None = None, pos_end: Pos | None = None) -> Self:
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context: Context | None = None) -> Self:
    self.context = context
    return self


class Mid(Null):
  def __str__(self) -> str:
    return "mid"
