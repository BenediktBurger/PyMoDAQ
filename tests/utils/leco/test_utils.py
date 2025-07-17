from typing import Any

import pytest

from pymodaq.control_modules.daq_move import DataActuator

from pymodaq.utils.leco.utils import (
    binary_serialization,
    binary_serialization_to_kwargs,
    thread_command_to_leco_tuple,
    leco_tuple_to_thread_command,
    ThreadCommand,
)


@pytest.mark.parametrize("value", (
        5,
        6.7,
        "some value",
))
def test_native_json_object_binary_serialization(value):
    serialized_tuple = binary_serialization(value)
    assert serialized_tuple[1] is None
    assert serialized_tuple[0] == value


class TestBinarySerialization:
    @pytest.fixture
    def serialized(self):
        value = DataActuator(data=10.5)
        return binary_serialization(value)

    def test_first_part_is_None(self, serialized):
        assert serialized[0] is None

    def test_second_part_is_list_of_bytes(self, serialized):
        assert isinstance(serialized[1][0], bytes)

    def test_is_as_expected(self, serialized):
        content = serialized[1][0]  # type: ignore
        # content at one point in time:
        expected = b"\x00\x00\x00\x0cDataActuator\x00\x00\x00\x05float\x00\x00\x00\x03<f8\x00\x00\x00\x08\x890\x82\x91\x1e\xd4\xd9A\x00\x00\x00\x03str\x00\x00\x00\x08actuator\x00\x00\x00\x03str\x00\x00\x00\x03raw\x00\x00\x00\x03str\x00\x00\x00\x06Data0D\x00\x00\x00\x03str\x00\x00\x00\x07uniform\x00\x00\x00\x04list\x00\x00\x00\x01\x00\x00\x00\x07ndarray\x00\x00\x00\x03<f8\x00\x00\x00\x08\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00%@\x00\x00\x00\x03str\x00\x00\x00\x00\x00\x00\x00\x04list\x00\x00\x00\x01\x00\x00\x00\x03str\x00\x00\x00\x04CH00\x00\x00\x00\x03str\x00\x00\x00\x00\x00\x00\x00\x04list\x00\x00\x00\x00\x00\x00\x00\x04list\x00\x00\x00\x00\x00\x00\x00\x04list\x00\x00\x00\x00\x00\x00\x00\x04list\x00\x00\x00\x00"
        # test part before and after timestamp, as timestamp varies
        assert content[:25] == expected[:25]
        assert content[48:] == expected[48:]


def test_binary_serialization_to_kwargs_simple():
    data = binary_serialization_to_kwargs(6.7)
    assert data == {"data": 6.7, "additional_payload": None}


@pytest.mark.parametrize(
    "obj, tup",
    (
        (7, (7, None)),
        (
            1 + 2j,
            (
                None,
                [
                    b"\x00\x00\x00\x07complex\x00\x00\x00\x04<c16\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@"
                ],
            ),
        ),
    ),
)
def test_binary_serialization(obj: Any, tup: tuple[Any, list[bytes]]):
    assert binary_serialization(obj) == tup


class Test_thread_command_leco_tuple_conversion:
    test_tuples: list[tuple[ThreadCommand, tuple[dict, list[bytes]]]] = [
        (
            ThreadCommand(command="command", attribute=[7]),
            ({"type": "ThreadCommand", "command": "command", "attribute": [7]}, []),
        ),
        (
            ThreadCommand(command="binary", attribute=[1 + 2j]),
            (
                {"type": "ThreadCommand", "command": "binary", "attribute": [None], "binary": [0]},
                [
                    b"\x00\x00\x00\x07complex\x00\x00\x00\x04<c16\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@"
                ],
            ),
        ),
    ]

    @pytest.mark.parametrize("tc, tup", test_tuples)
    def test_to_tuple(self, tc, tup):
        assert thread_command_to_leco_tuple(tc) == tup

    @pytest.mark.xfail(True, reason="requires ThreadCommand comparison in pymodaq_utils")
    @pytest.mark.parametrize("tc, tup", test_tuples)
    def test_to_tc(self, tc, tup):
        assert leco_tuple_to_thread_command(*tup) == tc