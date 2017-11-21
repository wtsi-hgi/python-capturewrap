from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Callable

from capture.models import CaptureResult


class CaptureBuilder:
    """
    TODO
    """
    @staticmethod
    def _capture_stdout(callable: Callable[..., CaptureResult]) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        stream = StringIO()
        with redirect_stdout(stream):
            return_value = callable()
        assert return_value.stdout is None, "stdout appears to have already been captured"
        return CaptureResult(return_value=return_value.return_value, stdout=stream.getvalue(),
                             stderr=return_value.stderr, exception=return_value.exception)

    @staticmethod
    def _capture_stderr(callable: Callable[..., CaptureResult]) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        stream = StringIO()
        with redirect_stderr(stream):
            return_value = callable()
        assert return_value.stderr is None, "stderr appears to have already been captured"
        return CaptureResult(return_value=return_value.return_value, stdout=return_value.stdout,
                             stderr=stream.getvalue(), exception=return_value.exception)

    @staticmethod
    def _capture_exception(callable: Callable[..., CaptureResult]) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        return_value = None
        exception = None
        try:
            return_value = callable()
            assert return_value.stderr is None, "stderr appears to have already been captured"
        except BaseException as e:
            exception = e
        return CaptureResult(return_value=return_value.return_value, stdout=return_value.stdout,
                             stderr=return_value.stderr, exception=exception)

    def __init__(self, capture_stdout: bool=False, capture_stderr: bool=False, capture_exception: bool=False):
        """
        TODO
        :param capture_stdout:
        :param capture_stderr:
        :param capture_exception:
        """
        self.capture_stdout = capture_stdout
        self.capture_stderr = capture_stderr
        self.capture_exception = capture_exception

    def build(self, callable: Callable, *args, **kwargs) -> Callable[..., CaptureResult]:
        """
        TODO
        :param callable:
        :param args:
        :param kwargs:
        :return:
        """
        def capturing_callable() -> CaptureResult:
            return CaptureResult(return_value=callable(*args, **kwargs))

        if self.capture_stdout:
            capturing_callable = CaptureBuilder._capture_stdout(capturing_callable)
        if self.capture_stderr:
            capturing_callable = CaptureBuilder._capture_stderr(capturing_callable)
        if self.capture_exception:
            capturing_callable = CaptureBuilder._capture_exception(capturing_callable)

        return capturing_callable
