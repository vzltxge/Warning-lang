from typing import Self


# Position
class Pos:
  def __init__(self, index: int, line_num: int, col_num: int, fn: str,
               ftxt: str) -> None:
    self.index = index
    self.line_num = line_num
    self.col_num = col_num
    self.fn, self.ftxt = fn, ftxt

  def advance(self, cc: str | None = None) -> Self:
    if cc == "\n":
      self.line_num += 1
      self.col_num = 0

    self.col_num, self.index = self.col_num + 1, self.index + 1
    return self

  def __repr__(self) -> str:
    return f"i:{self.index}, l:{self.line_num}, c:{self.col_num}, f:{self.fn}"

  def copy(self) -> "Pos":
    return Pos(self.index, self.line_num, self.col_num, self.fn, self.ftxt)
