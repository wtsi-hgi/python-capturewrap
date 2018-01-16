import sys
import unittest

import itertools
from typing import NamedTuple, Callable, Optional, Any

from capturewrap import CaptureWrapBuilder
from capturewrap.models import RETURN_VALUE_TEXT, STDOUT_TEXT, STDERR_TEXT, EXCEPTION_TEXT

_SENTINEL = "not-set"


class _CaptureConfiguration(NamedTuple):
    build_flag: Optional[str]
    test_method: Callable
    captured_attribute: str
    expected_value: Any


class _ComparableException(Exception):
    def __eq__(self, other):
        if not isinstance(other, _ComparableException):
            return False
        return other.args == self.args

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(id(self))

def _combine_values(*args):
    return " ".join(args)


INPUT_ARGS = ("hello ", )
INPUT_KWARGS = {"kwarg": "world"}
RETURN_VALUE_IDENTIFIER = f"{RETURN_VALUE_TEXT}: "
STDOUT_VALUE_IDENTIFIER = f"{STDOUT_TEXT}: "
STDERR_VALUE_IDENTIFIER = f"{STDERR_TEXT}: "
EXCEPTION_VALUE_IDENTIFIER = f"{EXCEPTION_TEXT}: "
EXCEPTION_TYPE = _ComparableException

_COMMON_OUTPUT = _combine_values("".join(INPUT_ARGS), "".join(INPUT_KWARGS.values()))
RETURN_OUTPUT = _combine_values(RETURN_VALUE_IDENTIFIER, _COMMON_OUTPUT)
STDOUT_OUTPUT = _combine_values(STDOUT_VALUE_IDENTIFIER, _COMMON_OUTPUT)
STDERR_OUTPUT = _combine_values(STDERR_VALUE_IDENTIFIER, _COMMON_OUTPUT)
EXCEPTION_OUTPUT = _combine_values(EXCEPTION_VALUE_IDENTIFIER, _COMMON_OUTPUT)


def _returner(arg, kwarg=_SENTINEL):
    return _combine_values(RETURN_VALUE_IDENTIFIER, arg, kwarg)

def _stdouter(arg, kwarg=_SENTINEL):
    sys.stdout.write(_combine_values(STDOUT_VALUE_IDENTIFIER, arg, kwarg))
    sys.stdout.flush()

def _stderrer(arg, kwarg=_SENTINEL):
    sys.stderr.write(_combine_values(STDERR_VALUE_IDENTIFIER, arg, kwarg))
    sys.stderr.flush()

def _exceptioner(arg, kwarg=_SENTINEL):
    raise EXCEPTION_TYPE(_combine_values(EXCEPTION_VALUE_IDENTIFIER, arg, kwarg))


class TestWrapCaptureBuilder(unittest.TestCase):
    """
    Tests for `WrapCaptureBuilder`.
    """
    _capture_configurations = {
        RETURN_VALUE_TEXT: _CaptureConfiguration(None, _returner, "return_value", RETURN_OUTPUT),
        STDOUT_TEXT: _CaptureConfiguration("capture_stdout", _stdouter, "stdout", STDOUT_OUTPUT),
        STDERR_TEXT: _CaptureConfiguration("capture_stderr", _stderrer, "stderr", STDERR_OUTPUT),
        EXCEPTION_TEXT: _CaptureConfiguration(
            "capture_exceptions", _exceptioner, "exception", EXCEPTION_TYPE(EXCEPTION_OUTPUT))
    }

    def test_capture_combinations(self):
        combinations = []
        for i in range(len(TestWrapCaptureBuilder._capture_configurations)):
            combinations.extend(itertools.combinations(TestWrapCaptureBuilder._capture_configurations.keys(), r=i + 1))

        for combination in combinations:
            with self.subTest(combination=combination):
                captures = [TestWrapCaptureBuilder._capture_configurations[configuration] for configuration in combination]
                build_combinations = [capture.build_flag for capture in captures if capture.build_flag is not None]
                builder_kwargs = {build_parameter: True for build_parameter in build_combinations}

                def callable(*args, **kwargs):
                    returns = []
                    # Execute callables, saving exception until last (else proceeding ones won't get called)
                    for test_method in sorted([capture.test_method for capture in captures],
                                               key=lambda x: int(x == _exceptioner)):
                        result = test_method(*args, **kwargs)
                        returns.append(result)
                    collapsed = ([x for x in returns if x is not None])
                    self.assertLessEqual(len(collapsed), 1, "More than one call returned a non-`None` value (has "
                                                            "`_returner` been called multiple times?)")
                    return None if len(collapsed) == 0 else collapsed[0]

                capturing = CaptureWrapBuilder(**builder_kwargs).build(callable)
                captured_result = capturing(*INPUT_ARGS, **INPUT_KWARGS)

                for capture in captures:
                    exception_and_return = TestWrapCaptureBuilder._capture_configurations[EXCEPTION_TEXT] in captures \
                                           and TestWrapCaptureBuilder._capture_configurations[RETURN_VALUE_TEXT] in captures
                    expected_value = capture.expected_value
                    if exception_and_return and capture.captured_attribute == RETURN_VALUE_TEXT:
                        expected_value = None
                    self.assertEqual(expected_value, getattr(captured_result, capture.captured_attribute), msg=capture)

    def test_exception_capture_when_no_exception(self):
        builder = CaptureWrapBuilder(capture_exceptions=True)
        wrapped = builder.build(_returner)
        result = wrapped(*INPUT_ARGS, **INPUT_KWARGS)
        self.assertEqual(RETURN_OUTPUT, result.return_value)

    def test_exception_capture_when_capturing_other_exception(self):
        builder = CaptureWrapBuilder(capture_exceptions=lambda e: False)
        wrapped = builder.build(_exceptioner)
        self.assertRaises(_ComparableException, wrapped, *INPUT_ARGS, **INPUT_KWARGS)

    def test_exception_capture_when_capturing_raised_exception(self):
        builder = CaptureWrapBuilder(capture_exceptions=lambda e: isinstance(e, EXCEPTION_TYPE))
        wrapped = builder.build(_exceptioner)
        result = wrapped(*INPUT_ARGS, **INPUT_KWARGS)
        self.assertIsInstance(result.exception, EXCEPTION_TYPE)

    def test_legacy_exception_capture_flag(self):
        builder = CaptureWrapBuilder(capture_exception=True)
        wrapped = builder.build(_exceptioner)
        result = wrapped(*INPUT_ARGS, **INPUT_KWARGS)
        self.assertIsInstance(result.exception, EXCEPTION_TYPE)

    def test_legacy_exception_capture_flag_with_new_flag(self):
        self.assertRaises(ValueError, CaptureWrapBuilder, capture_exception=False, capture_exceptions=True)


if __name__ == "__main__":
    unittest.main()
