"""Asyncio protocol implementation of RFplayer."""

import asyncio
from datetime import timedelta
from fnmatch import fnmatchcase
from functools import partial
import logging
from typing import Any, Callable, Coroutine, Optional, Sequence, Tuple, Type

from serial_asyncio import create_serial_connection

from .rfpparser import (
    PacketType,
    decode_packet,
    encode_packet,
    packet_events,
    valid_packet,
)

log = logging.getLogger(__name__)

TIMEOUT = timedelta(seconds=5)


class ProtocolBase(asyncio.Protocol):
    """Manage low level rfplayer protocol."""

    transport = None  # type: asyncio.BaseTransport

    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        disconnect_callback: Optional[Callable[[Optional[Exception]], None]] = None,
        options: Optional[Sequence[dict]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize class."""
        self.options = options
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()
        self.packet = ""
        self.buffer = ""
        self.packet_callback = None  # type: Optional[Callable[[PacketType], None]]
        self.disconnect_callback = disconnect_callback

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Just logging for now."""
        self.transport = transport
        # self.send_raw_packet("ZIA++HELLO")

    def init_commands(self) -> None:
        """Just logging for now."""
        #self.transport = transport
        self.send_raw_packet("ZIA++HELLO. PING")
        for command in self.options.get('START_COMMANDS',[]):
            self.send_raw_packet("ZIA++"+command)

    def data_received(self, data: bytes) -> None:
        """Add incoming data to buffer."""
        try:
            decoded_data = data.decode()
        except UnicodeDecodeError:
            invalid_data = data.decode(errors="replace")
            log.warning("Error during decode of data, invalid data: %s", invalid_data)
        else:
            self.buffer += decoded_data
            self.handle_lines()

    def handle_lines(self) -> None:
        """Assemble incoming data into per-line packets."""
        while "\n\r" in self.buffer:
            line, self.buffer = self.buffer.split("\n\r", 1)
            if valid_packet(line):
                self.handle_raw_packet(line)
            else:
                log.warning("dropping invalid data: %s", line)

    def handle_raw_packet(self, raw_packet: str) -> None:
        """Handle one raw incoming packet."""
        raise NotImplementedError()

    def send_raw_packet(self, packet: str) -> None:
        """Encode and put packet string onto write buffer."""
        data = bytes(packet + "\n\r", "utf-8")
        log.debug("writing data: %s", repr(data))
        self.transport.write(data)  # type: ignore

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """Log when connection is closed, if needed call callback."""
        if exc:
            log.exception("disconnected due to exception")
        else:
            log.info("disconnected because of close/abort.")
        if self.disconnect_callback:
            self.disconnect_callback(exc)


class PacketHandling(ProtocolBase):
    """Handle translating rfplayer packets to/from python primitives."""

    def __init__(
        self,
        *args: Any,
        packet_callback: Optional[Callable[[PacketType], None]] = None,
        options: Optional[Sequence[dict]] = None,
        **kwargs: Any,
    ) -> None:
        """Add packethandling specific initialization.
        packet_callback: called with every complete/valid packet
        received.
        """
        super().__init__(*args, **kwargs)
        self.options = options
        if packet_callback:
            self.packet_callback = packet_callback

    def handle_raw_packet(self, raw_packet: str) -> None:
        """Parse raw packet string into packet dict."""
        packets = []
        try:
            packets = decode_packet(raw_packet)
        except BaseException:
            log.exception("failed to parse packet data: %s", raw_packet)

        if packets:
            for packet in packets:
                if packet != None:
                    if "ok" in packet:
                        # handle response packets internally
                        log.debug("command response: %s", packet)
                        self.handle_response_packet(packet)
                    else:
                        log.debug("handle packet: %s", packet)
                        self.handle_packet(packet)
        else:
            log.warning("no valid packet, ou ZIA66 = Retour Info")

    def handle_packet(self, packet: PacketType) -> None:
        """Process incoming packet dict and optionally call callback."""
        if self.packet_callback:
            # forward to callback
            self.packet_callback(packet)
        else:
            log.debug("packet with no callback %s", packet)

    def handle_response_packet(self, packet: PacketType) -> None:
        """Handle response packet."""
        raise NotImplementedError()

    def send_packet(self, fields: PacketType) -> None:
        """Concat fields and send packet to gateway."""
        encoded_packet = encode_packet(fields)
        self.send_raw_packet(encoded_packet)

    def send_command(
        self,
        protocol: str,
        command: str,
        device_address: str = None,
        device_id: str = None,
    ) -> None:
        """Send device command to rfplayer gateway."""

        if device_id is not None and device_address is None:
            if protocol == "EDISIOFRAME" : # le device_id contient la cde
                self.send_raw_packet(f"ZIA++{protocol} {device_id}")
            else :
                self.send_raw_packet(f"ZIA++{command} ID {device_id} {protocol}")
        elif device_address is not None:
            if command == "DIM":
                if device_id is None: #sinon le device_id devient le % du DIM
                    if protocol == "RTS" or protocol == "X2DSHUTTER":
                        DIM_ADDON="%4"
                        self.send_raw_packet(f"ZIA++{command} {protocol} {device_address} {DIM_ADDON}")
                else:
                    self.send_raw_packet(f"ZIA++{command} {device_address} {protocol} %{device_id} ") #le device_id devient le % du DIM
            else:
                self.send_raw_packet(f"ZIA++{command} {device_address} {protocol}")
        else:
            self.send_raw_packet(f"ZIA++{command}")

    def send_raw_command(
        self,
        command: str,
    ) -> None:
        self.send_raw_packet(f"{command}")

class CommandSerialization(PacketHandling):
    """Logic for ensuring asynchronous commands are sent in order."""

    def __init__(
        self,
        *args: Any,
        packet_callback: Optional[Callable[[PacketType], None]] = None,
        options: Optional[Sequence[dict]] = None,
        **kwargs: Any,
    ) -> None:
        """Add packethandling specific initialization."""
        super().__init__(*args, **kwargs)
        self.options = options
        if packet_callback:
            self.packet_callback = packet_callback
        self._event = asyncio.Event()
        self._lock = asyncio.Lock()

    def handle_response_packet(self, packet: PacketType) -> None:
        """Handle response packet."""
        self._last_ack = packet
        self._event.set()

    async def send_command_ack(
        self,
        protocol: str,
        command: str,
        device_address: str = None,
        device_id: str = None,
    ) -> bool:
        """Send command, wait for gateway to repond."""
        async with self._lock:
            self.send_command(protocol, command, device_address, device_id)
            self._event.clear()
            # await self._event.wait()
        return True
    
    async def send_raw_command_ack(
        self,
        command: str,
    ) -> bool:
        """Send command, wait for gateway to repond."""
        async with self._lock:
            self.send_raw_command(command)
            self._event.clear()
            # await self._event.wait()
        return True


class EventHandling(PacketHandling):
    """Breaks up packets into individual events with ids'.

    Most packets represent a single event (light on, measured
    temperature), but some contain multiple events (temperature and
    humidity). This class adds logic to convert packets into individual
    events each with their own id based on packet details (protocol,
    switch, etc).
    """

    def __init__(
        self,
        *args: Any,
        event_callback: Optional[Callable[[PacketType], None]] = None,
        ignore: Optional[Sequence[str]] = None,
        options: Optional[Sequence[dict]] = None,
        **kwargs: Any,
    ) -> None:
        """Add eventhandling specific initialization."""
        super().__init__(*args, **kwargs)
        self.event_callback = event_callback
        self.options = options
        # suppress printing of packets
        log.debug("EventHandling")
        if not kwargs.get("packet_callback"):
            self.packet_callback = lambda x: None
        if ignore:
            log.debug("ignoring: %s", ignore)
            self.ignore = ignore
        else:
            self.ignore = []

    def _handle_packet(self, packet: PacketType) -> None:
        """Event specific packet handling logic."""
        events = packet_events(packet)
        for event in events:
            if self.ignore_event(event["id"]):
                log.debug("ignoring event with id: %s", event)
                continue
            log.debug("got event: %s", event)
            if self.event_callback:
                self.event_callback(event)
            else:
                self.handle_event(event)

    def handle_event(self, event: PacketType) -> None:
        """Handle of incoming event (print)."""
        log.debug("_handle_event")
        string = "{id:<32} "
        if "command" in event:
            string += "{command}"
        if "cover" in event:
            string += "{cover}"
        if "platform" in event:
            string += "{platform}"
        elif "version" in event:
            if "hardware" in event:
                string += "{hardware} {firmware} "
            string += "V{version} R{revision}"
        else:
            string += "{value}"
            if event.get("unit"):
                string += " {unit}"

        print(string.format(**event))

    def handle_packet(self, packet: PacketType) -> None:
        """Apply event specific handling and pass on to packet handling."""
        self._handle_packet(packet)
        super().handle_packet(packet)

    def ignore_event(self, event_id: str) -> bool:
        """Verify event id against list of events to ignore."""
        for ignore in self.ignore:
            if fnmatchcase(event_id, ignore):
                log.debug("ignore_event")
                return True
        return False


class RfplayerProtocol(CommandSerialization, EventHandling):
    """Combine preferred abstractions that form complete Rflink interface."""


def create_rfplayer_connection(
    port: str,
    baud: int = 115200,
    protocol: Type[ProtocolBase] = RfplayerProtocol,
    packet_callback: Optional[Callable[[PacketType], None]] = None,
    event_callback: Optional[Callable[[PacketType], None]] = None,
    disconnect_callback: Optional[Callable[[Optional[Exception]], None]] = None,
    ignore: Optional[Sequence[str]] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    options: Optional[Sequence[dict]] = None
) -> "Coroutine[Any, Any, Tuple[asyncio.BaseTransport, ProtocolBase]]":
    """Create Rflink manager class, returns transport coroutine."""
    if loop is None:
        loop = asyncio.get_event_loop()
    # use default protocol if not specified
    protocol_factory = partial(
        protocol,
        loop=loop,
        packet_callback=packet_callback,
        event_callback=event_callback,
        disconnect_callback=disconnect_callback,
        ignore=ignore if ignore else [],
        options=options,
    )

    # setup serial connection
    conn = create_serial_connection(loop, protocol_factory, port, baud)

    return conn
