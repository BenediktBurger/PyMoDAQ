
from pyleco.core.message import Message, MessageTypes
from pyleco.core.data_message import DataMessage
from pyleco.json_utils.json_objects import ErrorResponse, ResultResponse, Request
from pyleco.json_utils.errors import RECEIVER_UNKNOWN, NODE_UNKNOWN
from pyleco.test import FakeCommunicator
import pytest
from pymodaq_utils.utils import ThreadCommand
from pymodaq.utils.leco.pymodaq_listener import ActorListener, PymodaqListener


name = "listener"

@pytest.fixture
def actorListener() -> ActorListener:
    listener = ActorListener(name=name)  # , context=FakeContext())  # type: ignore
    listener.communicator = FakeCommunicator(name=name)  # type: ignore[assign]
    return listener

@pytest.fixture
def Listener() -> PymodaqListener:
    listener = Listener(name=name)  # , context=FakeContext())  # type: ignore
    listener.communicator = FakeCommunicator(name=name)  # type: ignore[assign]
    return listener


class TestSendRPCToRemote:
    remote_name = "receiver"

    def test_send_message_successfully(self, actorListener: ActorListener):
        actorListener.set_remote_name(self.remote_name)
        actorListener.communicator._r = [  # type: ignore[assign]
            Message(
                name,
                self.remote_name,
                message_type=MessageTypes.JSON,
                data=ResultResponse(1, None),
            )
        ]
        actorListener.send_rpc_message_to_remote("whatever")
        sent: Message = actorListener.communicator._s[0]  # type: ignore
        expected_sent = Message(
            self.remote_name,
            name,
            data=Request(1, "whatever"),
            header=sent.header,
        )
        assert expected_sent == sent
        assert self.remote_name in actorListener.remote_names

    @pytest.mark.parametrize("error", (RECEIVER_UNKNOWN, NODE_UNKNOWN))
    def test_unreachable_receiver_removes_receiver(self, actorListener: ActorListener, error):
        actorListener.set_remote_name(self.remote_name)
        actorListener.communicator._r = [  # type: ignore[assign]
            Message(
                name,
                self.remote_name,
                message_type=MessageTypes.JSON,
                data=ErrorResponse(None, error=error),
            )
        ]
        actorListener.send_rpc_message_to_remote("whatever")
        assert self.remote_name not in actorListener.remote_names


@pytest.mark.parametrize(
    "tc, message",
    (
        (
            ThreadCommand("command", [8]),
            DataMessage.from_frames(
                b"listener",
                b"",
                b'{"type":"ThreadCommand","command":"command","attribute":[8]}',
            ),
        ),
        (
            ThreadCommand("command", [1 + 2j]),
            DataMessage.from_frames(
                b"listener",
                b"",
                b'{"type":"ThreadCommand","command":"command","attribute":[null],"binary":[0]}',
                b"\x00\x00\x00\x07complex\x00\x00\x00\x04<c16\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@",
            ),
        ),
    ),
)
def test_create_thread_command_message(
    listener: PymodaqListener, tc: ThreadCommand, message: DataMessage
):
    m = listener.create_thread_command_message(tc)
    assert m.topic == message.topic
    print(m.payload[0])
    assert m.data == message.data
    assert m.payload[1:] == message.payload[1:]


@pytest.mark.parametrize(
    "payload, message",
    (
        (
            7,
            DataMessage("listener", data={"type": "Signal", "name": "signal", "content": 7}),
        ),
        (
            1 + 2j,
            DataMessage.from_frames(
                b"listener",
                b"",
                b'{"type": "Signal", "name": "signal", "content": null}',
                b"\x00\x00\x00\x07complex\x00\x00\x00\x04<c16\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\xf0?\x00\x00\x00\x00\x00\x00\x00@",
            ),
        ),
    ),
)
def test_abc(listener: PymodaqListener, payload, message: DataMessage):
    m = listener.create_signal_message("signal", signal_payload=payload)
    assert m.topic == message.topic
    assert m.data == message.data
    assert m.payload[1:] == message.payload[1:]
