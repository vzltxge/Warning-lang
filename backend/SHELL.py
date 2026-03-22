# NOTE: This is the code for the warning-lang programming language, made by Jason Yawson.
from frontend.LEXER import Lexer
from frontend.PARSER import ParseResult, Parser
from backend.INTERPRETER import Interpreter, Context, SymbolTable, RuntimeNumber
import sys
import ctypes
from runtime.null import Null, Mid

global_symbol_table: SymbolTable = SymbolTable("global")

# NOTE: This is for null variables, they are like Python's None
global_symbol_table.set("null", Null(), True)
global_symbol_table.set("mid", Mid(), True)  # null

# NOTE: This is for true variables
global_symbol_table.set("true", RuntimeNumber(ctypes.c_uint8(1)), True)
global_symbol_table.set("nocap", RuntimeNumber(ctypes.c_uint8(1)), True)  # true

# NOTE: This is for representing false
global_symbol_table.set("false", RuntimeNumber(ctypes.c_uint8(0)), True)
global_symbol_table.set("cap", RuntimeNumber(ctypes.c_uint8(0)), True)  # false
"""Debug flags"""
dbg_lex: bool = True  # NOTE: Prints tokens for debugging
dbg_parse: bool = False  # NOTE: Makes an ast.warn_dbg file for debugging

# Run function

def run(fn: str, text: str | None):
  if text is None:
    return None
  global_symbol_table.name += f"_<{fn}>"
  lexer: Lexer = Lexer(fn, text)
  tokens, error = lexer.get_tokens()
  if error:
    return error
  if dbg_lex:
    for token in tokens:
      print(token)
  """Generate AST"""
  parser: Parser = Parser(tokens)
  ast: ParseResult = parser.parse()
  if ast.error:
    return ast
  if dbg_parse:
    with open("testing/ast.warn_dbg", "w") as f:
      f.write(f"tokens[{len(tokens)}]: __format__ = Type, Contained:\n\n")
      for node in ast.node:
        f.write(repr(node))
  """Run program"""

  interpreter: Interpreter = Interpreter()
  context: Context = Context("<program>")
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)
  return result


if __name__ == "__main__":
  text: str | None = None
  assert len(sys.argv) > 1, "REPL is not supported"
  with open(sys.argv[1], "r") as f:
    print(f"Interpreting: {sys.argv[1]} [file]\n")
    text = f.read()
  result = run(f"{sys.argv[1]}", text)
  if result.error:
    print(result.error)
  elif result.value:
    # Use a simple function to print everything in the result list
    def print_results(val):
      if isinstance(val, list):
        for item in val:
          print_results(item)
      elif val is not None:
        print(val)

    print_results(result.value)
