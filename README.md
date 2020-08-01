# pymage_size
[![CircleCI](https://circleci.com/gh/kobaltcore/pymage_size.svg?style=svg)](https://circleci.com/gh/kobaltcore/pymage_size)
[![Downloads](https://pepy.tech/badge/pymage_size)](https://pepy.tech/project/pymage_size)

A Python package for getting the dimensions of an image without loading it into memory. No external dependencies either!

## Disclaimer
This library is currently in Beta. This means that the interface might change and that not all possible edge cases have been properly tested.

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
