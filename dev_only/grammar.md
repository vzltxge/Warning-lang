comp_ops = LT,GT, L_EQ, G_EQ, DOUBLE_EQ, NOT_EQ

expr    :  KEYWORD:VAR IDENT EQ EXPR
        : comp (AND|OR comp)*

comp      : arith-expr(comp_op arith_expr) *
          :not comp
        
arth-expr: term ((PLUS|MINUS) term)*

term    : factor ((MUL|DIV) factor)*

factor	: (PLUS|MINUS) factor
				: power
				
power	: call (POW factor)*

call: atom (LPAREN, (expr)?, RPAREN)

atom 	: INT|FLOAT
  		: LPAREN expr RPAREN
  		: if-expr
      : func-def

if-expr : IF LPAREN expr RPAREN LBRACE expr RBRACE
        (ELSEIF LPAREN expr RPAREN LBRACE expr RBRACE)* 
        (ELSE LBRACE expr RBRACE)?


func-def: FN:KEYWORD IDENTIFIER?
  LPAREN (IDENTIFIER, ...) RPAREN

  
AND should have less precedence than arth-expr
Comparison should have more precedence than var assignment but less than term, factor and power


Comparison OP's

true = 1
false = 0
OR: return true if at least one is true
AND: return true if both are true
NOT: reverse condition
