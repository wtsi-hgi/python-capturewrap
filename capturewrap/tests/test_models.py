import unittest

from capturewrap.models import CaptureResult

_EXAMPLE_RETURN_VALUE = "2"
_EXAMPLE_STDOUT = "example-1"
_EXAMPLE_STDERR = "example-2"
_EXAMPLE_EXCEPTION = ValueError()


class TestCaptureResult(unittest.TestCase):
    """
    Tests for `CaptureResult`.
    """
    def setUp(self):
        self.capture_result = CaptureResult(return_value=_EXAMPLE_RETURN_VALUE, stdout=_EXAMPLE_STDOUT,
                                            stderr=_EXAMPLE_STDERR, exception=_EXAMPLE_EXCEPTION)

    def test_str_when_all_none(self):
        self.assertIsInstance(str(self.capture_result), str)
