import ctypes
from typing import Any, Self, TypeAlias

from middle_end.ERRORS import RTError
from middle_end.POSITION import Pos
from runtime.typemap import type_map
from typechecking.TYPECHECKER import TypeChecker

"""Number class to help with number ops"""
num_type: TypeAlias = (ctypes.c_int64
                       | ctypes.c_int32
                       | ctypes.c_int16
                       | ctypes.c_int8
                       | ctypes.c_int64
                       | ctypes.c_float
                       | ctypes.c_double
                       | ctypes.c_uint8
                       | ctypes.c_uint16
                       | ctypes.c_uint32
                       | ctypes.c_uint64
)

class Context:
  ... # NOTE: Use interpreter's Context, but don't import it otherwise there will be an import error

class RuntimeNumber:
  def __init__(self, value: num_type) -> None:
    self.value = value
    self.set_pos()
    self.set_context()
    self.type_: type = type(value)
  def is_true(self) -> bool:
    # We are using ctypes module so use .value.value instead of .value
    return self.value.value != 0

  def operate(self, other, operation: str) -> Any:
    if isinstance(other, RuntimeNumber):
      whole_num_types: tuple = (ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint64, ctypes.c_int8, ctypes.c_int16, ctypes.c_int32, ctypes.c_int64, ctypes.c_uint8)
      decimal_types: tuple = (ctypes.c_float, ctypes.c_double)
      type_1 = type(self.value)
      type_2 = type(other.value)
      type_ = TypeChecker().promote_type(type_1, type_2)

      # NOTE: variable conv_type is the type you convert the value to when performing operations
      conv_type = float  # If no type is found, it defaults to float
      result_value = None
      if type_ in whole_num_types:
        conv_type = int
      elif type_ in decimal_types:
        conv_type = float
      if type(self.value) in whole_num_types + decimal_types:
        match operation:
          case "+":
            if conv_type is int:
              result_value = int(self.value.value) + int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) + float(other.value.value)
          case "-":
            if conv_type is int:
              result_value = int(self.value.value) - int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) - float(other.value.value)
          case "*":
            if conv_type is int:
              result_value = int(self.value.value) * int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) * float(other.value.value)
          case "/":
            if other.value.value == 0 or other.value.value == 0.0:
              # Creating position if None
              start_pos: Pos = (other.pos_start
                                if other.pos_start is not None else
                                (self.pos_start if self.pos_start is not None
                                 else Pos(0, 0, 0, "<unknown>", "")))
              end_pos: Pos = (self.pos_end if self.pos_end is not None else
                              (other.pos_end if other.pos_end is not None else
                               Pos(0, 0, 0, "<unknown>", "")))

              return None, RTError(
                  pos_start=start_pos,
                  pos_end=end_pos,
                  details="Division by zero",
                  context=self.context,
              )
            if conv_type is int:
              result_value = int(self.value.value) / int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) / float(other.value.value)
          case "^":
            if conv_type is int:
              result_value = int(self.value.value)**int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value)**float(other.value.value)

          case "<":
            if conv_type is int:
              result_value = int(self.value.value) < int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) < float(other.value.value)
          case ">":
            if conv_type is int:
              result_value = int(self.value.value) > int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) > float(other.value.value)
          case ">=":
            if conv_type is int:
              result_value = int(self.value.value) >= int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) >= float(
                  other.value.value)
          case "<=":
            if conv_type is int:
              result_value = int(self.value.value) <= int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) <= float(
                  other.value.value)
          case "==":
            if conv_type is int:
              result_value = int(self.value.value) == int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) == float(
                  other.value.value)
          case "!=":
            if conv_type is int:
              result_value = int(self.value.value) != int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) != float(
                  other.value.value)
          case "&&":
            if conv_type is int:
              result_value = int(self.value.value) and int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) and float(
                  other.value.value)
          case "||":
            if conv_type is int:
              result_value = int(self.value.value) or int(other.value.value)
            elif conv_type is float:
              result_value = float(self.value.value) or float(
                  other.value.value)
          case "!":
            if conv_type is int:
              result_value = not int(self.value.value)
            elif conv_type is float:
              result_value = not float(self.value.value)
        result_value = type_(result_value)
        return result_value

  def set_pos(self,
              pos_start: Pos | None = None,
              pos_end: Pos | None = None) -> Self:
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

  def __repr__(self) -> str:
    return f"{type_map.get(self.type_)}({self.value.value})"
