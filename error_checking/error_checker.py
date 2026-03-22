from typing import TypeAlias

from frontend.TOKENS import TT

tt_list: TypeAlias = list[TT]


def _find_longest_match(
  a: tt_list, b: tt_list, a_lo: int, a_hi: int, b_lo: int, b_hi: int
) -> tuple[int, int, int]:
  # Build lookup: element -> [indices in b where it appears]
  b2j: dict[TT, list[int]] = {}
  for j, elem in enumerate(b[b_lo:b_hi], b_lo):
    b2j.setdefault(elem, []).append(j)

  best_i, best_j, best_size = a_lo, b_lo, 0
  j2len: dict[int, int] = {}

  for i in range(a_lo, a_hi):
    new_j2len: dict[int, int] = {}
    for j in b2j.get(a[i], []):
      if j < b_lo:
        continue
      # extend any existing match ending at j-1, or start fresh
      k = new_j2len[j] = j2len.get(j - 1, 0) + 1
      if k > best_size:
        best_i, best_j, best_size = i - k + 1, j - k + 1, k
    j2len = new_j2len

  return best_i, best_j, best_size


def _get_matching_blocks(a: tt_list, b: tt_list) -> list[tuple[int, int, int]]:
  matches: list[tuple[int, int, int]] = []

  def recurse(a_lo: int, a_hi: int, b_lo: int, b_hi: int) -> None:
    i, j, size = _find_longest_match(a, b, a_lo, a_hi, b_lo, b_hi)
    if size == 0:
      return
    if a_lo < i and b_lo < j:
      recurse(a_lo, i, b_lo, j)  # left of match
    matches.append((i, j, size))
    if i + size < a_hi and j + size < b_hi:
      recurse(i + size, a_hi, j + size, b_hi)  # right of match

  recurse(0, len(a), 0, len(b))
  return matches


class Rule:
  def __init__(self, name: str, pattern: tt_list) -> None:
    self.name, self.pattern = name, pattern
    
  def __repr__(self) -> str:
    return f"{self.name} and the pattern is ({self.pattern})"
    
  def edit_dist(self, a: tt_list, b: tt_list) -> int:
    # Levenshtein distance — min insertions/deletions/substitutions
    # to turn token list a into token list b
    rows, cols = len(a) + 1, len(b) + 1
    dp = [[0] * cols for _ in range(rows)]

    for i in range(rows):
      dp[i][0] = i
    for j in range(cols):
      dp[0][j] = j

    for i in range(1, rows):
      for j in range(1, cols):
        if a[i - 1] == b[j - 1]:
          dp[i][j] = dp[i - 1][j - 1]  # tokens match, free
        else:
          dp[i][j] = 1 + min(
            dp[i - 1][j],  # deletion
            dp[i][j - 1],  # insertion
            dp[i - 1][j - 1],  # substitution
          )
    return dp[-1][-1]

  def match(self, tokens: tt_list) -> tuple[bool, float]:
    # Get all non-overlapping matching blocks between
    # this rule's pattern and the given token list
    blocks = _get_matching_blocks(self.pattern, tokens)

    # Sum matched tokens and compute Gestalt ratio
    matched = sum(size for _, _, size in blocks)
    total = len(self.pattern) + len(tokens)
    score = (2 * matched / total) if total else 1.0

    exact = tokens == self.pattern
    return (exact, score)


def did_you_mean(tokens: tt_list, rules: list[Rule], cutoff: float = 0.6) -> list[Rule]:
  # Quick upper bound check before running the full algorithm —
  # same idea as SequenceMatcher's real_quick_ratio:
  # if even the best possible score can't beat the cutoff, skip it
  def real_quick_ratio(pattern: tt_list) -> float:
    total = len(pattern) + len(tokens)
    return (2 * min(len(pattern), len(tokens)) / total) if total else 1.0

  scored: list[tuple[float, Rule]] = []

  for rule in rules:
    # cheap check first — bail early if impossible to beat cutoff
    if real_quick_ratio(rule.pattern) < cutoff:
      continue

    exact, score = rule.match(tokens)
    if exact:
      return [rule]  # perfect match, no need to check further
    if score >= cutoff:
      scored.append((score, rule))

  scored.sort(reverse=True)
  return [rule for _, rule in scored]
