import ctypes
from typing import Any

type_map: dict[Any, str] = {
  ctypes.c_int64: "i64",
  ctypes.c_int32: "i32",
  ctypes.c_int16: "i16",
  ctypes.c_int8: "i8",
  
  ctypes.c_float: "f32",
  ctypes.c_double: "f64",

  ctypes.c_uint8: "u8",
  ctypes.c_uint16: "u16",
  ctypes.c_uint32: "u32",
  ctypes.c_uint64: "u64",
}
inverse_type_map: dict[str, Any] = {v: k for k, v in type_map.items()}