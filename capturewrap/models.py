import json
from traceback import format_exception_only
from typing import Any


RETURN_VALUE_TEXT = "return_value"
STDOUT_TEXT = "stdout"
STDERR_TEXT = "stderr"
EXCEPTION_TEXT = "exception"


class CaptureResult:
    """
    Captured result.
    """
    def __init__(self, return_value: Any=None, stdout: str=None, stderr: str=None, exception: BaseException=None):
        self.return_value = return_value
        self.stdout = stdout
        self.stderr = stderr
        self.exception = exception

    def __str__(self):
        store = {}
        if self.return_value is not None:
            store[RETURN_VALUE_TEXT] = str(self.return_value)
        if self.stdout is not None:
            store[STDOUT_TEXT] = self.stdout
        if self.stderr is not None:
            store[STDERR_TEXT] = self.stderr
        if self.exception is not None:
            store[EXCEPTION_TEXT] = format_exception_only(type(self.exception), self.exception)
        return json.dumps(store)
