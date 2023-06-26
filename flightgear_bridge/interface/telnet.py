from typing import Optional

import telnetlib3
from loguru import logger
from telnetlib3 import TelnetReaderUnicode, TelnetWriterUnicode

from flightgear_bridge.interface.base import BaseInterface

CRLF = "\r\n"


class TelnetInterface(BaseInterface):
    """A wrapper around a telnet connection to FlightGear."""

    reader: TelnetReaderUnicode
    writer: TelnetWriterUnicode

    def __init__(self, reader: TelnetReaderUnicode, writer: TelnetWriterUnicode):
        """Create a new TelnetInterface."""
        self.reader = reader
        self.writer = writer

    async def ls(self, directory: Optional[str] = None):
        """List properties."""
        await self._send_command("ls" if directory is None else f"ls {directory}")
        return await self._get_response()

    async def dump(self):
        """Dump current state as XML."""
        await self._send_command("dump")
        return await self._get_response()

    async def cd(self, directory: str):
        """Change directory."""
        await self._send_command(f"cd {directory}")
        return await self._get_response()

    async def pwd(self):
        """Display current path."""
        await self._send_command("pwd")
        return await self._get_response()

    async def get(self, path: str):
        """Retrieve the value of a parameter."""
        await self._send_command(f"get {path}")
        return await self._get_response()

    async def set(self, path: str, value: str):
        """Set variable to a new value."""
        await self._send_command(f"set {path} {value}")
        return await self._get_response()

    async def quit(self):
        """Terminate connection."""
        await self._send_command("quit")
        self.writer.close()
        return await self.writer.protocol.waiter_closed

    async def _send_command(self, cmd: str):
        """Send a command to FlightGear."""
        logger.debug(f"Sending command: {cmd}")
        self.writer.write(cmd + CRLF)
        await self.writer.drain()

    async def _get_response(self):
        """Get a response from FlightGear."""
        response = (await self.reader.readuntil(CRLF.encode())).decode("utf-8").strip()
        logger.debug(f"Received response: {response}")
        return response

    async def await_closure(self):
        """Wait for connection closure."""
        return await self.writer.protocol.waiter_closed

    async def close(self):
        """Close the connection."""
        self.writer.close()
        self.reader.feed_eof()

    @staticmethod
    async def connect(host: str, port: int):
        """Connect to a FlightGear telnet interface."""
        reader, writer = await telnetlib3.open_connection(host, port)
        logger.info(f"Telnet connection established to {host}:{port}")
        return TelnetInterface(reader, writer)
