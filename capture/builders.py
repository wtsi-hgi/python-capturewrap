from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Callable

from capture.models import CaptureResult


class CaptureBuilder:
    """
    TODO
    """
    @staticmethod
    def _capture_stdout(callable: Callable[..., CaptureResult], *args, **kwargs) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        stream = StringIO()
        with redirect_stdout(stream):
            return_value = callable(*args, **kwargs)
        assert return_value.stdout is None, "stdout appears to have already been captured"
        return CaptureResult(return_value=return_value.return_value, stdout=stream.getvalue(),
                             stderr=return_value.stderr, exception=return_value.exception)

    @staticmethod
    def _capture_stderr(callable: Callable[..., CaptureResult], *args, **kwargs) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        stream = StringIO()
        with redirect_stderr(stream):
            return_value = callable(*args, **kwargs)
        assert return_value.stderr is None, "stderr appears to have already been captured"
        return CaptureResult(return_value=return_value.return_value, stdout=return_value.stdout,
                             stderr=stream.getvalue(), exception=return_value.exception)

    @staticmethod
    def _capture_exception(callable: Callable[..., CaptureResult], *args, **kwargs) -> CaptureResult:
        """
        TODO
        :param callable:
        :return:
        """
        try:
            return_value = callable(*args, **kwargs)
            assert return_value.exception is None, "exception appears to have already been captured"
            return CaptureResult(return_value=return_value.return_value, stdout=return_value.stdout,
                                 stderr=return_value.stderr)
        except BaseException as e:
            return CaptureResult(exception=e)

    @staticmethod
    def _wrap(callable: Callable, wrapper: Callable) -> Callable:
        """
        TODO
        :param callable:
        :param wrapper:
        :return:
        """
        def wrapped(*args, **kwargs):
            return wrapper(callable, *args, **kwargs)
        return wrapped

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

    def build(self, callable: Callable) -> Callable[..., CaptureResult]:
        """
        TODO
        :param callable:
        :param args:
        :param kwargs:
        :return:
        """
        def capturing_callable(*args, **kwargs) -> CaptureResult:
            return CaptureResult(return_value=callable(*args, **kwargs))

        if self.capture_exception:
            # Need to capture exceptions first else other (non-return) captured information will be lost
            capturing_callable = CaptureBuilder._wrap(capturing_callable, CaptureBuilder._capture_exception)
        if self.capture_stdout:
            capturing_callable = CaptureBuilder._wrap(capturing_callable, CaptureBuilder._capture_stdout)
        if self.capture_stderr:
            capturing_callable = CaptureBuilder._wrap(capturing_callable, CaptureBuilder._capture_stderr)


        return capturing_callable
