import ctypes
from typing import Any
from middle_end.ERRORS import TypeError_
class TypeChecker:
  def __init__(self) -> None:
    lowest_rank = 0
    self.__type_map: dict[Any, dict[str, Any]] = {
        ctypes.c_ushort: {
          "rank": 0,
          "ctype": ctypes.c_ushort,
        },
        ctypes.c_ulong: {
          "rank": lowest_rank + 1,
          "ctype": ctypes.c_ulong,
        },
        ctypes.c_ulonglong: {
          "rank": lowest_rank + 2,
          "ctype": ctypes.c_ulonglong,
        },
        ctypes.c_short: {
            "rank": lowest_rank + 3,
            "ctype": ctypes.c_int16
        },
        ctypes.c_long: {
            "rank": lowest_rank + 4,
            "ctype": ctypes.c_int32
        },
        ctypes.c_longlong: {
            "rank": lowest_rank + 5,
            "ctype": ctypes.c_int64
        },
        ctypes.c_float: {
            "rank": lowest_rank + 6,
            "ctype": ctypes.c_double
        },
        ctypes.c_double: {
          "rank": lowest_rank + 7,
          "ctype": ctypes.c_double,
        },
    }
  
  """t1 is the first type you enter and t2 is the second type you are meant to enter"""

  def promote_type(self, t1, t2) -> Any:
    return t1 if self.__type_map[t1]["rank"] >= self.__type_map[t2]["rank"] else t2

  def check_type(self, node, type) -> TypeError_ | None:
    if node.type != type:
      return TypeError_(
          pos_start=node.pos_start,
          pos_end=node.pos_end,
          details=f"Expected type {type}, got {node.type}",
      )
  def is_size_of_value_valid(self, type_, value, object) -> bool:
    INT_RANGES: dict[Any,tuple[int, int]] = {
      ctypes.c_int8: (-256, 255),
      ctypes.c_int16: (-32_768, 32_767),
      ctypes.c_int32: (-2_147_483_648, 2_147_483_647),
      ctypes.c_int64: (-9_223_372_036_854_775_808, 9_223_372_036_854_775_807),
    }
    UINT_RANGES = {
        ctypes.c_uint8:  (0, 255),
        ctypes.c_uint16: (0, 65_535),
        ctypes.c_uint32: (0, 4_294_967_295),
        ctypes.c_uint64: (0, 18_446_744_073_709_551_615),
    }
    
    FLOAT_RANGES = {
      ctypes.c_float: (1.1754943508222875e-38, 3.4028234663852886e+38),
      ctypes.c_double: (2.2250738585072014e-308, 1.7976931348623157e+308)
    }
    if type_ in INT_RANGES:
      min_, max_ = INT_RANGES[type_]
    elif type_ in UINT_RANGES:
      min_, max_= UINT_RANGES[type_]
    elif type_ in FLOAT_RANGES:
      min_,max_ = FLOAT_RANGES[type_]
    
    if object.checked_size:
      return True
    object.checked_size = True
    return min_ <= value <= max_
