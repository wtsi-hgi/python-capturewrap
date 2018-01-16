from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Callable, Optional, Union

from capturewrap.models import CaptureResult

_CAPTURE_EXCEPTION_SENTINEL = object()


class CaptureWrapBuilder:
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
    def _capture_exceptions(callable: Callable[..., CaptureResult], *args, **kwargs) -> CaptureResult:
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
    def _create_capture_exceptions(capture_decider: Callable[[BaseException], bool]) -> Callable:
        """
        Creates exception capturer using given capture decider.
        :param capture_decider: given the exception as the first arguments, decides whether it should be captured or
        not (and hence raised)
        :return:
        """
        def wrapped(*args, **kwargs):
            result = CaptureWrapBuilder._capture_exceptions(*args, **kwargs)
            if result.exception is not None:
                if not capture_decider(result.exception):
                    raise result.exception
            return result

        return wrapped

    @staticmethod
    def _wrap(method: Callable, wrapper: Callable) -> Callable:
        """
        Wraps the given callable method in the given wrapper, passing through the callable's arguments to the wrapper.
        :param method: the callable method to wrap
        :param wrapper: the wrapper to wrap callable with
        :return:
        """
        def wrapped(*args, **kwargs):
            return wrapper(method, *args, **kwargs)
        return wrapped

    @property
    def capture_exceptions(self) -> Callable[[BaseException], bool]:
        return self._capture_exceptions

    @capture_exceptions.setter
    def capture_exceptions(self, capture_exceptions: Union[bool, Callable[[BaseException], bool]]):
        if isinstance(capture_exceptions, bool):
            self._capture_exceptions = lambda e: capture_exceptions
        else:
            self._capture_exceptions = capture_exceptions

    def __init__(self, capture_stdout: bool=False, capture_stderr: bool=False,
                 capture_exceptions: Union[bool, Callable[[BaseException], bool]]=False,
                 capture_exception: bool=_CAPTURE_EXCEPTION_SENTINEL):
        """
        Constructor.
        :param capture_stdout: whether to capture the content on stdout
        :param capture_stderr: whether to capture the content on sterr
        :param capture_exceptions: whether to capture exceptions (returns on an exception, oppose to raising the
        exception) or, more specifically, to capture an exception if a given callable dictates (else let it raise).
        Useful for capturing `SystemExit(code=0)`
        """
        if capture_exception != _CAPTURE_EXCEPTION_SENTINEL:
            # TODO: warning that `capture_exception` is deprecated
            if capture_exceptions:
                raise ValueError("Both `capture_exception` and `capture_exceptions` cannot be set together "
                                 "(`capture_exception` is deprecated)")
            capture_exceptions = capture_exception

        self.capture_stdout = capture_stdout
        self.capture_stderr = capture_stderr
        self._capture_exceptions = None
        self.capture_exceptions = capture_exceptions

    def build(self, callable: Callable) -> Callable[..., CaptureResult]:
        """
        Build a method that captures the required information when the given callable is called.
        :param callable: the callable to capture information from
        :return: the wrapped callable
        """
        def capturing_callable(*args, **kwargs) -> CaptureResult:
            return CaptureResult(return_value=callable(*args, **kwargs))

        if self.capture_exceptions:
            # Need to capture exceptions first else other (non-return) captured information will be lost
            exceptions_wrapper = CaptureWrapBuilder._create_capture_exceptions(self.capture_exceptions)
            capturing_callable = CaptureWrapBuilder._wrap(capturing_callable, exceptions_wrapper)
        if self.capture_stdout:
            capturing_callable = CaptureWrapBuilder._wrap(capturing_callable, CaptureWrapBuilder._capture_stdout)
        if self.capture_stderr:
            capturing_callable = CaptureWrapBuilder._wrap(capturing_callable, CaptureWrapBuilder._capture_stderr)

        return capturing_callable
