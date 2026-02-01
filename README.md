
Run code using uv run py -m backend.SHELL testing/code.th
You can also make a thing debug file which ends in th_dbg
I kind of borrowed rust syntax especially with the ... operator and the types


Thing-lang was made in python and developent started on January 4th 2026.
This is the thing programming language, btw it is interpreted.
This is written in python and i used the ctypes module: If you want suggest other modules for types i could have used.
It is a statically typed language.
I made it static because:
- It is easier to optimize the code when the type is known at before runtime
- It is easier to debug the code.


Types
  #NOTE: Soon implement these

  str

  #Implemented
  -i16 -> c_short
  -i32 -> c_long
  -i64 -> c_longlong
  -dec -> c_float
  -u8 -> ubyte
  -u16 -> ushort
  -u32 -> uint
  -u64 -> ulong
  -i8-> byte

# Note: The dec keyword is decimal-ish, it is not as precise as python's decimal.Decimal but it has around 6-7 digits of precision.

I did not add a 67 reference but unfortunately, That is the precision of the decimal type in thing-lang.

It uses the IEEE 754 32-bit standard for floating-point numbers.
The standard is OK in terms of precision, but it is fast and efficient.

If you use an i64 type for a variable and you overflow it, it will not just silently wrap around. It will raise an error. Which most programming language should do.

This also happens for other types like i32 and i16. Personally, I think it is a good practice to handle such errors gracefully instead of silently wrapping around.

By default, thing uses ctypes.c_int64 for integers and ctypes.c_float for floating-point numbers.
If you add an i16 to a i32, it will promote the type of the result to i32.

The promotion is as follows:

---

u8 -> u16 -> u32 -> u64 -> i16 -> i32 -> i64 -> f32 -> f64

---


If Statements:
if condition {
  expression/statement
};

There are also for and while loops:
 - For loops have a required step variable and you should use the step keyword.
 - For loops have a range and you use the ... operator  while Rust-lang uses ..
 - While loops do not have a step variable.


Btw all statements and expressions must end in ;