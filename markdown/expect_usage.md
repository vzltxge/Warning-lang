# `expect()` Function Usage Guide

Your `expect()` function is defined in [frontend/PARSER.py](../frontend/PARSER.py#L41) and validates that the current token matches an expected type and/or value.

## Current Implementation
```python
def expect(self, type_, value=None, message: str = "") -> InvalidSyntaxError | None:
    while self.current_token.type is TT.NEWLINE or self.current_token.type is TT.WS:
      self.advance()
    if not self.current_token.type == type_ and self.current_token.value != value:
      return InvalidSyntaxError(...)
```

## Places Where `expect()` Should Be Used

### 1. **`factor()` method** - Line 105-109
**Current code:**
```python
if self.current_token.type == TT.RPAREN:
    res.register_advancement()
    self.advance()
    return res.success(expr)
else:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected ')'",
        ))
```
**Should use:** `expect(TT.RPAREN, message="Expected ')'")` before advancing

---

### 2. **`while_stmt()` method** - Line 224-230
**Current code (checking for LBRACE):**
```python
if self.current_token.type != TT.LBRACE:
    return res.failure(InvalidSyntaxError(
        details="Bro you are missing a `{`!",
        pos_start=pos_start, pos_end=self.current_token.pos_end
    ))
```
**Should use:** `expect(TT.LBRACE, message="Bro you are missing a `{`!")`

**Current code (checking for RBRACE):** - Line 236-241
```python
if self.current_token.type != TT.RBRACE:
    return res.failure(InvalidSyntaxError(
        details="Bro you are missing a `}`!",
        pos_start=pos_start, pos_end=self.current_token.pos_end
    ))
```
**Should use:** `expect(TT.RBRACE, message="Bro you are missing a `}`!")`

---

### 3. **`for_expr()` method** - Multiple locations

**Line 253-258 (checking for IDENT):**
```python
if self.current_token.type != TT.IDENT:
    return res.failure(InvalidSyntaxError(
        details=f"
        Expected a variable/indentifier not {self.current_token}",
        pos_start=pos_start, pos_end=self.current_token.pos_end
    ))
```
**Should use:** `expect(TT.IDENT, message="Expected a variable/identifier")`

**Line 264-270 (checking for 'in' keyword):**
```python
if not self.current_token.matches(TT.KEYWORD, "in"):
    return res.failure(InvalidSyntaxError(
        details=f"Expected `in` keyword not {self.current_token}",
        pos_start=pos_start, pos_end=self.current_token.pos_end
    ))
```
**Should use:** `expect(TT.KEYWORD, value="in", message="Expected `in` keyword")`

**Line 283-287 (checking for LBRACE):**
```python
if self.current_token.type != TT.LBRACE:
    return res.failure(
        InvalidSyntaxError(pos_start=self.current_token.pos_start, pos_end=self.current_token.pos_end, details="Expected `{`")
    )
```
**Should use:** `expect(TT.LBRACE, message="Expected `{`")`

**Line 292 (already uses `expect()`):** ✅
```python
self.expect(TT.RBRACE, message="Expected `}` after for loop block")
```

---

### 4. **`make_var()` method** - Multiple locations

**Line 321-327 (checking for IDENT):**
```python
if self.current_token.type != TT.IDENT:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected identifier",
        ))
```
**Should use:** `expect(TT.IDENT, message="Expected identifier")`

**Line 332-339 (checking for EQ):**
```python
if self.current_token.type != TT.EQ:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '=' not " + str(self.current_token.value),
        ))
```
**Should use:** `expect(TT.EQ, message="Expected '='")`

---

### 5. **`if_expr()` method** - Multiple locations

**Line 423-430 (if block - checking for LBRACE):**
```python
if self.current_token.type != TT.LBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '{', Next time add it or else",
        ))
```
**Should use:** `expect(TT.LBRACE, message="Expected '{'")`

**Line 435-442 (if block - checking for RBRACE):**
```python
if self.current_token.type != TT.RBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '}', Next time add it or else",
        ))
```
**Should use:** `expect(TT.RBRACE, message="Expected '}'")`

**Line 456-463 (elif block - checking for LBRACE):**
```python
if self.current_token.type != TT.LBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '{', Next time add it or else",
        ))
```
**Should use:** `expect(TT.LBRACE, message="Expected '{'")`

**Line 469-476 (elif block - checking for RBRACE):**
```python
if self.current_token.type != TT.RBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '}', Next time add it or else",
        ))
```
**Should use:** `expect(TT.RBRACE, message="Expected '}'")`

**Line 486-493 (else block - checking for LBRACE):**
```python
if self.current_token.type != TT.LBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '{'",
        ))
```
**Should use:** `expect(TT.LBRACE, message="Expected '{'")`

**Line 499-506 (else block - checking for RBRACE):**
```python
if self.current_token.type != TT.RBRACE:
    return res.failure(
        InvalidSyntaxError(
            self.current_token.pos_start,
            self.current_token.pos_end,
            "Expected '}'",
        ))
```
**Should use:** `expect(TT.RBRACE, message="Expected '}'")`

---

## Summary

**Total locations to update: 18 places**

- `factor()`: 1
- `while_stmt()`: 2
- `for_expr()`: 4 (1 already uses it ✅)
- `make_var()`: 2
- `if_expr()`: 9

## Notes

- The `expect()` function currently returns an error or None. You should integrate it into the `res.register_advancement()` and `self.advance()` pattern used throughout the parser.
- Consider whether `expect()` should be modified to also handle the `register_advancement()` call automatically.
- Make sure error messages are consistent across all usages.
