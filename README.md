[![Build Status](https://travis-ci.org/wtsi-hgi/python-capturewrap.svg)](https://travis-ci.org/wtsi-hgi/python-capturewrap)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/python-capturewrap/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/python-capturewrap)

# Method Capture
_Wraps callables to capture stdout, stderr, exceptions and the return._


## Why?
This library was created to assist in the testing of Python code, where return values and exceptions are important, in 
addition to what is written to stdout and stderr. It allows for a callable to be ran without the caller being concerned 
with how important outputs are captured. 

An example use is when writing common code to test both a Python interface and a corresponding CLI (tested by invoking 
`main`). A common test procedure - which may involve a complex setup and tear down - can be ran using the different 
interfaces and return results that encapsulate the outputs, without concern over the form they take (e.g. the Python 
interface may have returned `True` on success but the `CLI` may have called `exit(0)`, with raises a `SystemExit` 
exception). 

Other [alternatives](#alternatives) exist for capturing stdout and stderr but none also handle exceptions.


## How?
```python
from capturewrap import CaptureWrapBuilder

builder = CaptureWrapBuilder(capture_stdout=True, capture_stderr=True, capture_exception=True)
wrapped = builder.build(my_method)

result = wrapped(*args, **kwargs)
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
print(f"return_value: {result.return_value}")
print(f"exception: {result.exception}")
```
Note: if an exception is captured, `return_value` will be `None`.


## Requirements
- Python >= 3.6

## Installation
Stable releases can be installed via [PyPI](https://pypi.python.org/pypi?name=capturewrap&:action=display):
```bash
$ pip install capturewrap
```

Bleeding edge versions can be installed directly from GitHub:
```bash
$ pip install git+https://github.com/wtsi-hgi/python-capturewrap.git@$commitOrBranch#egg=capturewrap
```

## Implementation
This implementation captures stdout and stdin using 
[`redirect_stdout`](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout) and 
[`redirect_stderr`](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stderr), which were added to 
the standard library in Python 3.5. 


## Alternatives
- [iocapture](https://github.com/oinume/iocapture): older solution, replaces `sys.stdout` and `sys.stderr` with 
capturing methods.
- [capturer](https://github.com/xolox/python-capturer): complex solution that works at lower level to intercept 
subprocess `stdout` and `stderr` using a pseudo terminal.
