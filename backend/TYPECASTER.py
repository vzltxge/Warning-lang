from typing import Any

class TypeCaster:
  def __init__(self) -> None:
    ...

  def cast_type(self, casting_type: Any, object_value: Any, object) -> Any:
    # NOTE: Use a match case stmt since different types haev acompatible types the can be casted to.
    if object.casted:
        return object_value
    object.casted = True
    return casting_type(object_value)