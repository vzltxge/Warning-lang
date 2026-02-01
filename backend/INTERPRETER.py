# Imports
import ctypes
from typing import Any, Never, Callable
from middle_end.AST import VarAssign
from runtime.number import RuntimeNumber
from middle_end.ERRORS import RTError, RTResult, VarSizeError, ReassigningConstError
from frontend.TOKENS import TT
from backend.TYPECASTER import TypeCaster
from typechecking.TYPECHECKER import TypeChecker
# End imports
# NOTE: Type checker, helps in type promotiong and checking if 2 things have the same type
tpchecker: TypeChecker = TypeChecker()
tpcaster: TypeCaster = TypeCaster()

"""
Symbol table class: Keeps track of variable names and their values
"""
class SymbolTable:
  def __init__(self) -> None:
    self.symbols: dict = {}
    self.parent: SymbolTable | None = None
    
    #NOTE: This is a dictionary that keeps track of if a variable is const or mut
    self.var_states: dict[str, bool] = {} 

  def get(self, name: str) -> Any:
    value = self.symbols.get(name, None)
    if value is None and self.parent:
      return self.parent.get(name)
    return value

  def set(self, name: str, value: Any) -> None:
    self.symbols[name] = value

  def remove(self, name: str) -> None:
    del self.symbols[name]
  def __repr__(self) -> str:
    return f"SymbolTable, {self.parent}, symbols={self.symbols}"


"""Context class to help with tracebacks"""


class Context:
  def __init__(self,
               display_name: str,
               parent=None,
               parent_entry_pos=None) -> None:
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table: SymbolTable = SymbolTable()


class Interpreter:
  # NOTE: Visits node and its children
  def visit(self, node, context: Context) -> RTResult:
    # Case 1: program / statements list
    res = RTResult()
    if isinstance(node, list):
      results = []
      for stmt in node:
        value = res.register(self.visit(stmt, context))
        if res.error:
          return res
        results.append(value)
      return res.success(results)

    # Case 2: single AST node
    method_name = f"visit_{type(node).__name__}"
    method = getattr(self, method_name, self.no_visit_method)
    # print(f"Method name: {method_name}")
    return method(node, context)

  def no_visit_method(self, node, context: Context) -> Never:
    raise Exception(f"No visit_{type(node).__name__} method defined")

  # Defining visit method for each node
  def visit_Number(self, node, context: Context) -> RTResult:
    res = RTResult()
    if not tpchecker.is_size_of_value_valid(type_=node.type_, value=node.token.value, object=node):
      return res.failure(VarSizeError(node.pos_start, node.pos_end))
    node.token.value = tpcaster.cast_type(casting_type=node.type_, object_value=node.token.value,object=node)
    return res.success(
        RuntimeNumber(node.token.value).set_context(context).set_pos(
            node.pos_start, node.pos_end))

  def visit_ForExpr(self, node, context: Context):
    res: RTResult = RTResult()
    start_value = res.register(self.visit(node.range.start, context))
    if res.error: return res

    end_value = res.register(self.visit(node.range.end, context))
    if res.error: return res

    if node.range.step:
      step_value = res.register(self.visit(node.range.step, context))
      if res.error: return res
    else:
      step_value = RuntimeNumber(ctypes.c_ubyte(1))

    i = start_value.value.value
    if step_value.value.value >= 0:
      condition: Callable[[], bool] = lambda: i < end_value.value.value
      # NOTE: If step is positive, we want to loop and end when i is not less than the end value
    else:
      condition: Callable[[], bool] = lambda: i > end_value.value.value
      # NOTE: If step is negative, we want to loop and end when i is not greater than the end value


    while condition():
      i += step_value.value.value
      context.symbol_table.set(node.var_name.value, RuntimeNumber(ctypes.c_longlong(i)))
      res.register(self.visit(node.block, context))
      if res.error:
        return res

    return res.success(None)
    
  def visit_WhileStmt(self, node, context):
    res = RTResult()
    while True:
      condition = res.register(self.visit(node.condition, context))
      if res.error:
        return res

      if not condition.is_true():
        break
      res.register(self.visit(node.block, context))
      if res.error:
        return res

    return res.success(None)

  def visit_Increment(self, node, context: Context) -> RTResult:
    res: RTResult = RTResult()
    value = self.visit_VarAccess(node.value, context)
    if node.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform increment operation on a constant variable", res=res)
    if node.postfix:
      old_value = value.value.value
      incremented_value: Any = ctypes.c_longlong(old_value.value + 1)
      context.symbol_table.set(node.value.var_name_token.value, RuntimeNumber(incremented_value))
      return res.success(RuntimeNumber(old_value))
    else:
      new_value = value.value.value.value + 1
      incremented_value: Any = ctypes.c_longlong(new_value)
      context.symbol_table.set(node.value.var_name_token.value, RuntimeNumber(incremented_value))
      return res.success(RuntimeNumber(incremented_value))
      
  def visit_IncrementBy(self, node: DecrementBy, context: Context) -> RTResult:
    res: RTResult = RTResult()
    node.value: VarAccess  # It is a variable
    node.amount: Number
    variable= self.visit_VarAccess(node.value, context)
    variable_value: int | float = variable.value.value.value #NOTE: This is the variables c_types value or the raw value
    
    if node.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform increment by operation on a constant variable", res=res)
      
    new_value = variable_value + node.amount.token.value
    variable_name = node.value.var_name_token.value
    context.symbol_table.set(variable_name, value=RuntimeNumber(variable.value.type_(new_value)))
    return res.success(None)
  def breaking_const_rule(self, node: VarAccess, msg: str, res: RTResult) -> RTResult:
      return res.failure(ReassigningConstError(details=msg, pos_start=node.pos_start, pos_end=node.pos_end))
      
  def visit_DecrementBy(self, node: DecrementBy, context: Context) -> RTResult:
    res: RTResult = RTResult()
    node.value: VarAccess  # It is a variable
    node.amount: Number
    
    variable= self.visit_VarAccess(node.value, context)
    variable_value: int | float = variable.value.value.value #NOTE: This is the variables c_types value or the raw value
    
    if node.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform decrement by operation on a constant variable", res=res)
      
    new_value = variable_value - node.amount.token.value
    variable_name = node.value.var_name_token.value
    context.symbol_table.set(variable_name, value=RuntimeNumber(variable.value.type_(new_value)))
    return res.success(None)
    
  def visit_MultiplyBy(self, node: MultiplyBy, context: Context) -> RTResult:
    res: RTResult = RTResult()
    node.value: VarAccess  # It is a variable
    node.amount: Number
    variable= self.visit_VarAccess(node.value, context)
    variable_value: int | float = variable.value.value.value #NOTE: This is the variables c_types value or the raw value
    
    if node.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform multiplication by operation on a constant variable", res=res)
      
    new_value = variable_value * node.amount.token.value
    variable_name = node.value.var_name_token.value
    context.symbol_table.set(variable_name, value=RuntimeNumber(variable.value.type_(new_value)))
    return res.success(None)
    
  def visit_DivideBy(self, node: DivideBy, context: Context) -> RTResult:
    res: RTResult = RTResult()
    node.value: VarAccess  # It is a variable
    node.amount: Number
    variable= self.visit_VarAccess(node.value, context)
    variable_value: int | float = variable.value.value.value #NOTE: This is the variables c_types value or the raw value
    
    if variable.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform division by operation on a constant variable", res=res)
      
    if node.amount.token.value == 0:
      return res.failure(RuntimeError("Division by zero", node.amount.pos_start, node.amount.pos_end))
    new_value = variable_value / node.amount.token.value 
    variable_name = node.value.var_name_token.value
    context.symbol_table.set(variable_name, value=RuntimeNumber(variable.value.type_(new_value)))
    return res.success(None)

  def visit_Decrement(self, node, context: Context) -> RTResult:
    res: RTResult = RTResult()
    value = self.visit_VarAccess(node.value, context)
    if node.value.is_const:
      return self.breaking_const_rule(node, msg="Cannot perform decrement operation on a constant variable", res=res)
    if node.postfix:
      old_value = value.value.value
      decremented_value: Any = old_value.value - 1
      decremented_value: Any = ctypes.c_longlong(decremented_value)
      context.symbol_table.set(node.value.var_name_token.value, RuntimeNumber(decremented_value))
      return res.success(RuntimeNumber(old_value))
    else:
      new_value = value.value.value.value - 1
      decremented_value: Any = ctypes.c_longlong(new_value)
      context.symbol_table.set(node.value.var_name_token.value, RuntimeNumber(decremented_value))
      return res.success(RuntimeNumber(decremented_value))

  def visit_VarAccess(self, node: VarAccess, context: Context) -> RTResult:
    res = RTResult()
    var_name = node.var_name_token.value
    value = context.symbol_table.get(var_name)
    is_const = context.symbol_table.var_states.get(var_name)
    node.is_const = is_const
    if not value:
      return res.failure(
          RTError(
              node.pos_start,
              node.pos_end,
              f"`{var_name}` is not defined",
              context,
          ))
    value = value.copy().set_pos(node.pos_start, node.pos_end)
    return res.success(value)

  def visit_VarAssign(self, node: VarAssign, context: Context) -> RTResult:
    res = RTResult()
    var_name = node.var_name_token.value
    value = res.register(self.visit(node.value_node, context))
    if res.error:
      return res
    if context.symbol_table.get(var_name) and context.symbol_table.var_states[var_name]:
        return res.failure(
            ReassigningConstError(
                node.pos_start,
                node.pos_end,
                f"`{var_name}` is already defined as const at start_pos={context.symbol_table.get(var_name).pos_start}, end_pos={context.symbol_table.get(var_name).pos_end}",
            ))
    context.symbol_table.set(var_name, value)
    context.symbol_table.var_states[var_name] = node.is_value_const
    return res.success(value)

  def visit_BinOp(self, node, context: Context) -> RTResult:
    res: RTResult = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.error: return res
    right = res.register(self.visit(node.right_node, context))
    if res.error: return res
    self.OPS_MAP = {
        # NOTE: a is left and b is right
        TT.PLUS: lambda a, b: a.added_to(b),
        TT.MINUS: lambda a, b: a.subbed_by(b),
        TT.MUL: lambda a, b: a.mult_by(b),
        TT.DIV: lambda a, b: a.divided_by(b),
        TT.POW: lambda a, b: a.powered_by(b),
        TT.EQ: lambda a, b: a.equals(b),
        TT.NOT_EQ: lambda a, b: a.not_equals(b),
        TT.LT: lambda a, b: a.less_than(b),
        TT.L_EQ: lambda a, b: a.less_than_or_equal(b),
        TT.GT: lambda a, b: a.greater_than(b),
        TT.G_EQ: lambda a, b: a.greater_than_or_equal(b),
        TT.AND: lambda a, b: a.anded_by(b),
        TT.OR: lambda a, b: a.ored_by(b),
    }
    operation: Callable = self.OPS_MAP.get(node.op_token.type)
    result, error = operation(left, right)
    # NOTE: Checks for errors
    if error: return res.failure(error)
    if result: return res.success(result.set_pos(node.pos_start, node.pos_end))
    return res.failure(
        RTError(node.pos_start, node.pos_end, "Unknown binary operation",
                context))

  def visit_UnaryOp(self, node, context: Context) -> RTResult:
    res: RTResult = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.error:
      return res
    error = None
    match node.op_tok.type:
      case TT.MINUS:
        number, error = number.mult_by(RuntimeNumber(ctypes.c_short(-1)))
      case TT.NOT:
        number, error = number.notted()
    if error:
      return res.failure(error)
    return res.success(number.set_pos(node.pos_start, node.pos_end))

  # In INTERPRETER.py

  def visit_IfExpr(self, node, context: Context) -> RTResult:
    res: RTResult = RTResult()

    for condition, expr in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.error:
        return res

      if condition_value.is_true():
        # expr is the list of nodes inside the { }
        expr_value = res.register(self.visit(expr, context))
        if res.error:
          return res
        return res.success(expr_value)

    if node.else_case:
      else_value = res.register(self.visit(node.else_case, context))
      if res.error:
        return res
      return res.success(else_value)

    return res.success(RuntimeNumber(ctypes.c_ushort(0)))
