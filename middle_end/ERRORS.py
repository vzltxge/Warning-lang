from abc import ABC, abstractmethod
from middle_end.POSITION import Pos
from middle_end.string_with_arrows import string_with_arrows
from typing import Any, Self


# Errors
class Error(ABC):
  @abstractmethod
  def __init__(self, pos_start: Pos, pos_end: Pos, error_name: str,
               details: str) -> None:
    self.error_name = error_name
    self.details = details
    self.pos_start, self.pos_end = pos_start, pos_end

  def __repr__(self) -> str:
    result: str = f"{self.error_name}: {self.details}"
    result += f", In {self.pos_start.fn}, line {self.pos_start.line_num}, col {self.pos_start.col_num + 1}"
    result += "\n\n" + string_with_arrows(self.pos_start.ftxt, self.pos_start,
                                          self.pos_end)
    return result


#  * Will be called by interpreter
class TypeError_(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str) -> None:
    super().__init__(
        pos_start=pos_start,
        pos_end=pos_end,
        error_name="TypeError",
        details=details,
    )



# * Will be called by lexer
class IllegalCharError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str) -> None:
    super().__init__(
        pos_start=pos_start,
        pos_end=pos_end,
        error_name="Illegal Character",
        details=details,
    )


class ExpectedCharError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str) -> None:
    super().__init__(pos_start, pos_end, "Expected char", details)


# Will be called by parser


class InvalidSyntaxError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str) -> None:
    super().__init__(
        pos_start=pos_start,
        pos_end=pos_end,
        error_name="Invalid Syntax",
        details=details,
    )

class RTResult:
  def __init__(self) -> None:
    self.value = None
    self.error = None

  def register(self, res) -> Any:
    if res.error:
      self.error = res.error
    return res.value

  def success(self, value) -> Self:
    self.value = value
    return self

  def failure(self, error) -> Self:
    self.error = error
    return self


class RTError(Error):
  def __init__(self,
               pos_start: Pos,
               pos_end: Pos,
               details: str = "",
               context=None) -> None:
    super().__init__(pos_start, pos_end, "Runtime Error", details)
    self.context = context

  def generate_traceback(self) -> str:
    result: str = ""
    pos = self.pos_start
    ctx = self.context
    while ctx:
      result += (
          f" File {pos.fn}, line {pos.line_num + 1}, in {ctx.display_name}\n"
          + result)
      pos = ctx.parent_entry_pos
      ctx = ctx.parent
    return "Traceback (most recent call last):\n" + result

  def __repr__(self) -> str:
    result: str = self.generate_traceback()
    result += f"{self.error_name}: {self.details}"
    result += "\n\n" + string_with_arrows(self.pos_start.ftxt, self.pos_start,
                                          self.pos_end)
    return result


# * This should be used by the interpreter when a variable is assigned a value where size is too large for the type to hold
class VarSizeError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str = "") -> None:
    super().__init__(pos_start, pos_end, "Variable Size Error", details)

# * This should be used by the parser when a statement is missing a semicolon
class MissingSemicolonError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str = "") -> None:
    super().__init__(pos_start, pos_end, "Missing Semicolon Error", details)

class ReassigningConstError(Error):
  def __init__(self, pos_start: Pos, pos_end: Pos, details: str = "") -> None:
    super().__init__(pos_start, pos_end, "Reassigning Constant Error", details)
