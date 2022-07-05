# pymage_size
[![Downloads](https://pepy.tech/badge/pymage_size)](https://pepy.tech/project/pymage_size)

A Python package for getting the dimensions of an image without loading it into memory. No external dependencies either!

## Installation
pymage_size is available from PyPI, so you can install via `pip`:
```bash
$ pip install pymage_size
```

## Usage
```python
from pymage_size import get_image_size

img_format = get_image_size("example.png")
width, height = img_format.get_dimensions()
```
