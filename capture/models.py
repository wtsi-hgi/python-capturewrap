class CaptureResult:
    """
    TODO
    """
    def __init__(self, return_value: Any=None, stdout: str=None, stderr: str=None, exception: BaseException=None):
        self.return_value = return_value
        self.stdout = stdout
        self.stderr = stderr
        self.exception = exception