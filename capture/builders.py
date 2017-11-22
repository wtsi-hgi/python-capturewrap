from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Callable

from capture.models import CaptureResult


class CaptureBuilder:
    """
    Builder of methods that capture information when a callable is called.
    """
    @staticmethod
    def _capture_stdout(callable: Callable[..., CaptureResult], *args, **kwargs) -> CaptureResult:
        """
        Captures content written to standard out.
        :param callable: the callable to wrap
        :param args: positional arguments passed to the callable
        :param kwargs: keyword arguments passed to the callable
        :return: the captured result
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
        Captures content written to standard error.
        :param callable: the callable to wrap
        :param args: positional arguments passed to the callable
        :param kwargs: keyword arguments passed to the callable
        :return: the captured result
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
        Captures exceptions, adding them to the captured result, opposed to raising them.
        :param callable: the callable to wrap
        :param args: positional arguments passed to the callable
        :param kwargs: keyword arguments passed to the callable
        :return: the captured result
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
        Wraps the given callable in the given wrapper, passing through the callable's arguments to the wrapper.
        :param callable: the callable to wrap
        :param wrapper: the wrapper to wrap callable with
        :return:
        """
        def wrapped(*args, **kwargs):
            return wrapper(callable, *args, **kwargs)
        return wrapped

    def __init__(self, capture_stdout: bool=False, capture_stderr: bool=False, capture_exception: bool=False):
        """
        Constructor.
        :param capture_stdout: whether to capture the content on stdout
        :param capture_stderr: whether to capture the content on sterr
        :param capture_exception: whether to capture exceptions (returns on an exception, oppose to error)
        """
        self.capture_stdout = capture_stdout
        self.capture_stderr = capture_stderr
        self.capture_exception = capture_exception

    def build(self, callable: Callable) -> Callable[..., CaptureResult]:
        """
        Build a method that captures the required information when the given callable is called.
        :param callable: the callable to capture information from
        :return: the wrapped callable
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
