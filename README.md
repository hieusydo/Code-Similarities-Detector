# Code Similarity

## Notes

Reference paper: http://theory.stanford.edu/~aiken/publications/papers/sigmod03.pdf

Winnowing:
- more fingerprints = higher chance of detecting duplicate pieces of codes even when variable and function names are changed
- how does space affect fingerprinting?
- grep just comments

Ignore C++ comments:

```sh
(\/\/.*)|(\/\*(.+\n)+\*\/)

diff <(grep -vE "(\/\/.*)|(\/\*(.+\n)+\*\/)" code_a.cpp) <(grep -vE "(\/\/.*)|(\/\*(.+\n)+\*\/)" code_b.cpp)

```

```py
# Filter single line comments and statements
filestr  = re.sub(r"(\/\/.*)|(using namespace .*)|(\#.*)", "", filestr)

# Remove whitespace
filestr = ' '.join(filestr.split())

# Remove multiline comments
filestr  = re.sub(r"(\/\/.*)|(\/\*(.*)\*\/)", "", filestr).strip()
```

## Observation
- Cheating signs:
  + Exact same comments
  + Same code structure: variable and function name change
- Winnowing reduce the computational cost when comparing codes (faster to compare hash value vs char by char)