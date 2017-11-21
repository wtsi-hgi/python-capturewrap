import json
from typing import Any


class CaptureResult:
    """
    TODO
    """
    def __init__(self, return_value: Any=None, stdout: str=None, stderr: str=None, exception: BaseException=None):
        self.return_value = return_value
        self.stdout = stdout
        self.stderr = stderr
        self.exception = exception

    def __str__(self):
        return json.dumps({
            "return_value": self.return_value,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "expcetion": self.exception})
