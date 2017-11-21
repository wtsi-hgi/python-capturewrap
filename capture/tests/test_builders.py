import sys
import unittest

import itertools

from capture import CaptureBuilder

_SENTINEL = "not-set"

class _ComparableException(Exception):
    """
    TODO
    """
    def __eq__(self, other):
        if not isinstance(other, _ComparableException):
            return False
        return other.args == self.args

    def __ne__(self, other):
        return not self.__eq__(other)

INPUT_ARGS = ("hello ", )
INPUT_KWARGS = {"kwarg": "world"}
RETURN_PREFIX = "return: "
STDOUT_PREFIX = "stdout: "
STDERR_PREFIX = "stderr: "
EXCEPTION_PREFIX = "exception: "
EXCEPTION_TYPE = _ComparableException

def _combine_values(*args):
    return " ".join(args)

_COMMON_OUTPUT = _combine_values("".join(INPUT_ARGS), "".join(INPUT_KWARGS.values()))
RETURN_OUTPUT = _combine_values(RETURN_PREFIX, _COMMON_OUTPUT)
STDOUT_OUTPUT = _combine_values(STDOUT_PREFIX, _COMMON_OUTPUT)
STDERR_OUTPUT = _combine_values(STDERR_PREFIX, _COMMON_OUTPUT)
EXCEPTION_OUTPUT = _combine_values(EXCEPTION_PREFIX, _COMMON_OUTPUT)

def _returner(arg, kwarg=_SENTINEL):
    return _combine_values(RETURN_PREFIX, arg, kwarg)

def _stdouter(arg, kwarg=_SENTINEL):
    sys.stdout.write(_combine_values(STDOUT_PREFIX, arg, kwarg))
    sys.stdout.flush()

def _stderrer(arg, kwarg=_SENTINEL):
    sys.stderr.write(_combine_values(STDERR_PREFIX, arg, kwarg))
    sys.stderr.flush()

def _exceptioner(arg, kwarg=_SENTINEL):
    raise EXCEPTION_TYPE(_combine_values(EXCEPTION_PREFIX, arg, kwarg))


class TestCaptureBuilder(unittest.TestCase):
    """
    TODO
    """
    # TODO: Change data structure
    _mappings = {
        "return_value": (None, _returner, ("return_value", RETURN_OUTPUT)),
        "stdout": ("capture_stdout", _stdouter, ("stdout", STDOUT_OUTPUT)),
        "stderr": ("capture_stderr", _stderrer, ("stderr", STDERR_OUTPUT)),
        "exception": ("capture_exception", _exceptioner, ("exception", EXCEPTION_TYPE(EXCEPTION_OUTPUT)))
    }

    def test_capture(self):
        permutations = []
        for i in range(len(TestCaptureBuilder._mappings)):
            permutations.extend(itertools.combinations(TestCaptureBuilder._mappings.keys(), r=i + 1))

        for permutation in permutations:
            with self.subTest(permutation=permutation):
                captures = [TestCaptureBuilder._mappings[configuration] for configuration in permutation]
                build_parameters = [capture[0] for capture in captures if capture[0] is not None]
                builder_kwargs = {build_parameter: True for build_parameter in build_parameters}

                def callable(*args, **kwargs):
                    returns = []
                    # Execute callables, saving exception until last (else proceeding ones won't get called)
                    for sub_callable in sorted([capture[1] for capture in captures],
                                               key=lambda x: int(x == _exceptioner)):
                        result = sub_callable(*args, **kwargs)
                        returns.append(result)
                    collapsed = ([x for x in returns if x is not None])
                    assert len(collapsed) <= 1, \
                        "More than one call returned a non-`None` value (has `_returner` been called multiple times?)"
                    return None if len(collapsed) == 0 else collapsed[0]

                capturing = CaptureBuilder(**builder_kwargs).build(callable)
                captured_result = capturing(*INPUT_ARGS, **INPUT_KWARGS)

                for capture in captures:
                    exception_and_return = TestCaptureBuilder._mappings["exception"] in captures \
                                           and TestCaptureBuilder._mappings["return_value"] in captures
                    attribute = capture[2][0]
                    expected_value = capture[2][1]
                    if exception_and_return and attribute == "return_value":
                        expected_value = None
                    self.assertEqual(expected_value, getattr(captured_result, attribute), msg=capture)


if __name__ == "__main__":
    unittest.main()
