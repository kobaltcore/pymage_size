# pymage_size
A Python package for getting the dimensions of an image without loading it into memory. No external dependencies either!

## Disclaimer
This library is currently in Beta. This means that the interface might change and that not all possible edge cases have been properly tested.

## Installation
py_midicsv is available from PyPI, so you can install via `pip`:
```bash
$ pip install pymage_size
```

## Usage
```python
from pymage_size import get_size

width, height = get_size("example.png")
```
