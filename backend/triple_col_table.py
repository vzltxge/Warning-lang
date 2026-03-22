from typing import Any


class TripleColTable:
  def __init__(self, name: str) -> None:
    self.row: dict[str, dict[str, Any | bool]] = {}
    self.name = name

  def add(self, name: str, value: Any, state: bool) -> None:
    self.row[name] = {"value": value, "state": state}

  def delete(self, name: str) -> None:
    del self.row[name]

  def get_state_of(self, name: str) -> bool:
    return self.row.get(name, {}).get("state", False)

  def get_value_of(self, name: str) -> Any:
    return self.row[name].get("value")

  def __repr__(self) -> str:
    return f"TripleColTable(name={self.row.keys()}, values={self.row.values()})"

  def __str__(self) -> str:
    return repr(self)
