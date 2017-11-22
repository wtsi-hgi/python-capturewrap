[![Build Status](https://travis-ci.org/wtsi-hgi/python-common.svg)](https://travis-ci.org/wtsi-hgi/python-baton-wrapper)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-baton-wrapper/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/python-baton-wrapper)

# Method Capture
_g_


## Why?
This library was created to assist in the testing of software that has a similar Python and CLI interface.


## How?
```python
from capturewrap import CaptureWrapBuilder, CaptureResult

builder = CaptureWrapBuilder(capture_stdout=True, capture_stderr=True, capture_exception=True)
wrapped = builder.build(my_method)

result = wrapped(*args, **kwargs)   # type: CaptureResult
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"return_value: {result.return_value}")
print(f"exception: {result.exception}")
```


## Requirements
- Python >= 3.6

## Installation
Stable releases can be installed via [PyPI](https://pypi.python.org/pypi?name=baton&:action=display):
```bash
$ pip install baton
```

Bleeding edge versions can be installed directly from GitHub:
```bash
$ pip3 install git+https://github.com/wtsi-hgi/python-baton-wrapper.git@<commit_id_or_branch_or_tag>#egg=baton
```


## Alternatives
- https://github.com/oinume/iocapture
- https://github.com/xolox/python-capturer
