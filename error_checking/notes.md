dp is a matrix.
Each cell stores an answer to a smaller problem.

dp[i][j] = minimum edits needed to turn
          a[:i] in b[:j]

a and b are both strings.
We are trying to turn a into b.

a = "123"
b = "12"

dp[1][1] = 0
dp[2][1] = 1 because we insert 3 here.

If len(a) = n and len(b) = m.
dp has (n+1) rows and (m+1) columns.
Because we include the empty prefix ""
a is the rows and m is the columns

We fill dp from top-left to bottom-right.
