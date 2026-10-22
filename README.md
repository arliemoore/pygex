# pygex

Pattern matcher coded in python that uses a Thompson NFA.

pygex was written to learn how regular expression engines work. It is not a
replacement for Python's built-in `re` module, which is much faster for
everyday patterns (see [Performance](#performance)). What pygex does have is
a guaranteed running time: a search takes time proportional to
`len(pattern) * len(text)`, so no pattern can make it hang.

## Getting Started

Requires Python 3.7 or newer and has no dependencies.

```python
from pygex import Pygex, PatternError

gex = Pygex('(hello|goodbye)? world')
gex.search('say hello world')  # True
gex.search('worl')             # False

Pygex('a**')                   # raises PatternError: multiple repeat at position 2
```

`search` finds the pattern anywhere in the text, like Python's `re.search`.
It returns only `True` or `False`; there is no match position or capture groups.

### Supported syntax

| Syntax  | Meaning                                  |
|---------|------------------------------------------|
| `a`     | The literal character `a`                |
| `.`     | Any single character                     |
| `ab`    | `a` followed by `b`                      |
| `a\|b`  | `a` or `b`                               |
| `a*`    | Zero or more `a`                         |
| `a+`    | One or more `a`                          |
| `a?`    | Zero or one `a`                          |
| `( )`   | Grouping                                 |
| `\x`    | Escape a special character, e.g. `\.` or `\(` |

`^ $ [ ] { }` and escapes like `\d` are not supported and raise a `PatternError`
rather than being silently treated as literals.

## How it works

1. **Parse** ([pygex/parser.py](pygex/parser.py)). The pattern is split into
   tokens, an explicit concatenation operator is inserted between adjacent
   pieces, and the shunting-yard algorithm converts it to postfix notation.
   For example `a|bc` becomes `abc·|`, where `·` is concatenation.
   `Pygex(pattern).postfix_string()` shows this form, which is handy for
   debugging.
2. **Build the NFA** ([pygex/nfa.py](pygex/nfa.py)). Each postfix token pushes
   or combines NFA fragments on a stack, following Thompson's construction.
3. **Search**. Instead of trying one path and backtracking, the NFA tracks
   every state it could be in at once. Each character of the text moves all of
   those states forward together, and a new attempt starts at every position
   so the pattern can match anywhere.

Because step 3 never backtracks, the work per character is bounded by the
number of states in the NFA.

## Performance

Measured with Python 3.9 on macOS. Times are per search call, with the
pattern compiled beforehand.

**Everyday patterns: `re` is far faster.** On an 11,000 character string:

| Pattern | pygex | re |
|---|---|---|
| `hello world` | 7.5 ms | 0.005 ms |
| `(hello\|goodbye) world` | 13.3 ms | 0.05 ms |
| `h.l+o w?orld` | 7.6 ms | 0.004 ms |

`re` is written in C and uses shortcuts like jumping straight to the first
fixed character of the pattern. pygex is pure Python and looks at every
character.

**Pathological patterns: pygex stays fast.** For the pattern `a?` repeated n
times followed by `a` repeated n times, searched in a string of n `a`s:

| n | pygex | re |
|---|---|---|
| 10 | 0.11 ms | 0.03 ms |
| 16 | 0.25 ms | 1.8 ms |
| 20 | 0.38 ms | 33 ms |
| 24 | 0.53 ms | 586 ms |

`re` backtracks, so its time roughly doubles every time n goes up by one.
pygex's time grows linearly. This is the same reason engines like
[RE2](https://github.com/google/re2) and Rust's
[regex](https://github.com/rust-lang/regex) crate use automata instead of
backtracking when patterns can come from untrusted users.

## Limitations

- Only reports whether a match exists, not where it is or what groups captured.
- No anchors (`^`, `$`), character classes (`[a-z]`, `\d`) or counted
  repetition (`{2,3}`).
- A `Pygex` object is not safe to search from several threads at once, because
  the search records bookkeeping on the NFA's states. Use one object per thread.

## Running the tests

```
python -m unittest
```

Besides the hand-written cases, the tests generate random patterns and check
that pygex agrees with Python's `re.search` on each one.

## Authors

* **Arlie Moore**

## License

No license has been chosen yet.

## Acknowledgments

1. https://swtch.com/~rsc/regexp/regexp1.html
    -  Detailed write up on Thompson NFA
2. https://gist.github.com/gmenard/6161825
    - Code in Java for how to convert pattern to postfix expression
