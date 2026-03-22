from typing import TypeAlias
import ctypes

num_type: TypeAlias = (
  ctypes.c_int64
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
  | ctypes.c_short
  | ctypes.c_ushort
)

whole_num_types: tuple = (
  ctypes.c_uint16,
  ctypes.c_uint32,
  ctypes.c_uint64,
  ctypes.c_int8,
  ctypes.c_int16,
  ctypes.c_int32,
  ctypes.c_int64,
  ctypes.c_uint8,
)
decimal_types: tuple = (ctypes.c_float, ctypes.c_double)
