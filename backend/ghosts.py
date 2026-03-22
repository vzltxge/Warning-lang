from enum import IntEnum
from typing import Any, final


class GhostRank(IntEnum):
  """
  The farther a ghosts value is from 3 determines how bad it is.
  The value of 1 means the ghost will lead to an error.
  The value of 2 means the ghost will lead ot a warning.
  The value of 3 means the ghost is OK.
  """

  NotDefined = 1


# NOTE: Ghost base class
class Ghost:
  @final
  def __repr__(self) -> str:
    # Get the name of the current class
    class_name: str = self.__class__.__name__
    # Get all attributes as a dictionary
    attributes: dict[str, Any] = self.__dict__
    # Format them into 'key=value' pairs
    attr: str = ", ".join([f"{k}={v!r}" for k, v in attributes.items()])
    return f"{class_name}({attr})"


# NOTE: Types of ghosts


# NOTE: For variables that are not defined
class NotDefined(Ghost):
  def __init__(self, name) -> None:
    self.name = name


# NOTE: Functions are not implemented yet
class EmptyFunction(Ghost):
  def __init__(self, name) -> None:
    self.name = name
