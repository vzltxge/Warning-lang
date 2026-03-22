from types_.num_types import num_type, whole_num_types, decimal_types
from typing import Any, Self, TypeAlias
from middle_end.ERRORS import RTError
from middle_end.POSITION import Pos
from types_.typemap import type_map
from typechecking.TYPECHECKER import TypeChecker
from runtime.context import Context

# FIX: Make code in operate function better and less repetitive.

"""Number class to help with number ops"""


class RuntimeNumber:
  def __init__(self, value: num_type) -> None:
    self.value = value
    self.set_pos()
    self.set_context()
    self.type_: type = type(value)

  def is_true(self) -> bool:
    # NOTE: We are using ctypes module so use .value.value instead of .value
    return self.value.value != 0

  def operate(self, other, operation: str) -> Any:
    if isinstance(other, RuntimeNumber):
      type_1 = type(self.value)
      type_2 = type(other.value)
      type_ = TypeChecker().promote_type(type_1, type_2)

      # NOTE: variable conv_type is the type you convert the value to when performing operations
      # If no type is found, it defaults to float
      result_value = None
      
      conv_type: TypeAlias = int
      if type_ not in whole_num_types:
        conv_type: TypeAlias = float
      if type_1 in whole_num_types + decimal_types:
        match operation:
          # NOTE: Arithmetic operators
          case "+":
            result_value = conv_type(self.value.value) + conv_type(other.value.value)
          case "-":
            result_value = conv_type(self.value.value) - conv_type(other.value.value)
          case "*":
            result_value = conv_type(self.value.value) * conv_type(other.value.value)
          case "/":
            if other.value.value == 0 or other.value.value == 0.0:
              # Creating position if None
              start_pos: Pos = (
                other.pos_start
                if other.pos_start is not None
                else (
                  self.pos_start
                  if self.pos_start is not None
                  else Pos(0, 0, 0, "<unknown>", "")
                )
              )
              end_pos: Pos = (
                self.pos_end
                if self.pos_end is not None
                else (
                  other.pos_end
                  if other.pos_end is not None
                  else Pos(0, 0, 0, "<unknown>", "")
                )
              )

              return None, RTError(
                pos_start=start_pos,
                pos_end=end_pos,
                details="Division by zero",
                context=self.context,
              )
            result_value = conv_type(self.value.value) / conv_type(other.value.value)
          case "^":
            result_value = conv_type(self.value.value) ** conv_type(other.value.value)

          # NOTE: Comparision operators
          case "<":
            result_value = conv_type(self.value.value) < conv_type(other.value.value)
          case ">":
            result_value = conv_type(self.value.value) > conv_type(other.value.value)
          case ">=":
            result_value = conv_type(self.value.value) >= conv_type(other.value.value)
          case "<=":
            result_value = conv_type(self.value.value) <= conv_type(other.value.value)
          case "==":
            result_value = conv_type(self.value.value) == conv_type(other.value.value)
          case "!=":
            result_value = conv_type(self.value.value) != conv_type(other.value.value)
          case "&&":
            result_value = conv_type(self.value.value) and conv_type(other.value.value)
          case "||":
            result_value = conv_type(self.value.value) or conv_type(other.value.value)
          case "!":
            result_value = not conv_type(self.value.value)
        result_value = type_(result_value)
        return result_value

  def set_pos(self, pos_start: Pos | None = None, pos_end: Pos | None = None) -> Self:
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context: Context | None = None) -> Self:
    self.context = context
    return self

  def added_to(self, other: Any):
    result_value = self.operate(other, "+")
    return RuntimeNumber(result_value).set_context(self.context), None

  def subbed_by(self, other: Any):
    result_value = self.operate(other, "-")
    return RuntimeNumber(result_value).set_context(self.context), None

  def mult_by(self, other: Any):
    result_value = self.operate(other, "*")
    return RuntimeNumber(result_value).set_context(self.context), None

  def pow_by(self, other: Any):
    result_value = self.operate(other, "^")
    return RuntimeNumber(result_value).set_context(self.context), None

  def div_by(self, other: Any):
    result_value = self.operate(other, "/")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_eq(self, other):
    result_value = self.operate(other, "==")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_not_eq(self, other):
    result_value = self.operate(other, "!=")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_lt(self, other):
    result_value = self.operate(other, "<")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_gt(self, other):
    result_value = self.operate(other, ">")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_l_eq(self, other):
    result_value = self.operate(other, "<=")
    return RuntimeNumber(result_value).set_context(self.context), None

  def comp_g_eq(self, other):
    result_value = self.operate(other, ">=")
    return RuntimeNumber(result_value).set_context(self.context), None

  def anded_by(self, other):
    result_value = self.operate(other, "&&")
    return RuntimeNumber(result_value).set_context(self.context), None

  def ored_by(self, other):
    result_value = self.operate(other, "||")
    return RuntimeNumber(result_value).set_context(self.context), None

  def notted(self):
    result_value = self.operate(None, "!")
    return RuntimeNumber(result_value).set_context(self.context), None

  def copy(self) -> "RuntimeNumber":
    copy = RuntimeNumber(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  # NOTE: This is not needed right now, may need in the future
  # def __hash__(self) -> int:
  #   return hash((self.value.value, self.type_))

  def __eq__(self, other) -> bool:
    return self.value.value == other.value.value and self.type_ == other.type_

  def __repr__(self) -> str:
    return f"{type_map.get(self.type_)}({self.value.value})"
