import asyncio
import datetime
import platform
import re
from os import path
from typing import Optional, List

import aiofiles
from aiocsv import AsyncWriter
from loguru import logger
from fastapi import WebSocket, APIRouter
from starlette.websockets import WebSocketDisconnect

from flightgear_bridge.config import config
from flightgear_bridge.interface.telnet import TelnetInterface

router = APIRouter()

DEFAULT_PARAMETERS = [
    "--aircraft=c172p",
    "--disable-random-objects",
    "--prop:/sim/rendering/random-vegetation=false",
    "--disable-ai-models",
    "--disable-ai-traffic",
    "--disable-real-weather-fetch",
    "--model-hz=120",  # Frequency of model updates
    "--bpp=32",
    "--wind=0@0",  # Wind speed and direction
    "--fog-fastest",
    "--turbulence=0",
    "--disable-terrasync",
    "--timeofday=noon",
    "--disable-fgcom",
    (
        f"--telnet=socket,out,{config.FLIGHT_GEAR_TELNET_POLLING_INTERVAL}"
        f",{config.FLIGHT_GEAR_TELNET_HOST}"
        f",{config.FLIGHT_GEAR_TELNET_PORT},udp"
    ),  # Telnet interface
]

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def get_flightgear_path():
    """Returns the path to the FlightGear executable"""
    if platform.system() == "Windows":
        return r"C:\Program Files\FlightGear 2020.3\bin\fgfs.exe"
    elif platform.system() == "Darwin":
        return "/Applications/FlightGear.app/Contents/MacOS/fgfs"
    else:
        return "/opt/flightgear/bin/fgfs"


async def pipe_stream_to_logger(stream: asyncio.StreamReader):
    async for line in stream:  # type: bytes
        stripped_line = ansi_escape.sub(
            "", str(line.decode("utf-8")).encode("ascii", "ignore").decode()
        ).strip()
        if stripped_line:
            logger.info(f"FlightGear: {stripped_line}")


class Controller:
    fg_process: Optional[asyncio.subprocess.Process]
    fg_interface: Optional[TelnetInterface]
    fg_path: Optional[str]
    fg_connected: bool
    logger_task: Optional[asyncio.Task]

    def __init__(self):
        self.fg_process = None
        self.fg_interface = None
        self.fg_path = get_flightgear_path()
        self.fg_connected = False
        self.logger_task = None

    async def monitor_fg_process(self, process: asyncio.subprocess.Process):
        stdout_pipe = asyncio.create_task(pipe_stream_to_logger(process.stdout))
        stderr_pipe = asyncio.create_task(pipe_stream_to_logger(process.stderr))

        await process.wait()
        stdout_pipe.cancel()
        stderr_pipe.cancel()

        logger.error(f"FlightGear process exited with code {process.returncode}")
        self.fg_process = None
        self.fg_connected = False
        if self.fg_interface is not None:
            await self.fg_interface.close()
        self.fg_interface = None

    async def set_fg_path(self, fg_path: str):
        self.fg_path = fg_path

    async def start_fg_process(self):
        if self.fg_path is None:
            raise Exception("FlightGear path not set")

        if self.fg_process is not None:
            self.fg_process.kill()

        self.fg_process = await asyncio.create_subprocess_exec(
            self.fg_path,
            *DEFAULT_PARAMETERS,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=path.dirname(self.fg_path),
        )

        asyncio.create_task(self.monitor_fg_process(self.fg_process))

    async def connect_fg(self):
        await self.disconnect_fg()
        self.fg_interface = await TelnetInterface.connect(
            config.FLIGHT_GEAR_TELNET_HOST, config.FLIGHT_GEAR_TELNET_PORT
        )
        self.fg_connected = True

    async def disconnect_fg(self):
        if self.fg_interface is not None:
            await self.fg_interface.close()
            self.fg_interface = None

    async def get_property_value(self, name: str):
        if self.fg_interface is None:
            raise Exception("FlightGear not connected")
        return await self.fg_interface.get_property(name)

    async def exit(self):
        await self.disconnect_fg()
        await self.stop_logger()
        if self.fg_process is not None:
            self.fg_process.kill()
            self.fg_process = None
        exit(0)

    async def start_logger(self, interval: float, properties: List[str]) -> str:
        await self.stop_logger()
        if self.fg_interface is None:
            raise Exception("FlightGear not connected")
        log_file_path = path.join(
            config.LOGS_DIR, f"log_{datetime.datetime.now().isoformat()}.log"
        )
        self.logger_task = asyncio.create_task(
            self._start_logger_worker(log_file_path, interval, properties)
        )
        return log_file_path

    async def stop_logger(self):
        if self.logger_task is not None:
            self.logger_task.cancel()
            self.logger_task = None

    @staticmethod
    def get_instance():
        if not hasattr(Controller, "_instance"):
            Controller._instance = Controller()
        return Controller._instance

    async def _start_logger_worker(
        self, log_file_path: str, interval: float, properties: List[str]
    ):
        async with aiofiles.open(
            log_file_path, mode="w", encoding="utf-8", newline=""
        ) as afp:
            writer = AsyncWriter(afp, dialect="unix")
            await writer.writerow(properties)
            while True:
                row = []
                for property_name in properties:
                    row.append(await self.fg_interface.get_property(property_name))
                await writer.writerow(row)
                await afp.flush()
                await asyncio.sleep(interval)


@router.websocket("/websocket")
async def read_users(websocket: WebSocket):
    await websocket.accept()
    controller = Controller.get_instance()
    logger.info("Websocket connection established")
    while True:
        result = "Error"
        try:
            data = (await websocket.receive_text()).strip()
        except WebSocketDisconnect:
            logger.info("Websocket connection closed")
            break
        logger.info(f"Received message: {data}")

        try:
            if data == "connect fg":
                await controller.connect_fg()
                result = "Connected"
            elif data == "disconnect fg":
                await controller.disconnect_fg()
                result = "Disconnected"
            elif data == "exit":
                await controller.exit()
            elif data.startswith("set_path:"):
                await controller.set_fg_path(data.partition(":")[2])
                result = "Path set"
            elif data == "start fg":
                await controller.start_fg_process()
                result = "FlightGear started"
            elif data == "stop_log":
                await controller.stop_logger()
                result = "Logging stopped"
            elif data.startswith("log:"):
                interval, _, properties = data.partition(":")[2].partition(":")
                log_file_path = await controller.start_logger(
                    float(interval), properties.split(",")
                )
                result = f"Logging to {log_file_path}"
            else:
                result = await controller.get_property_value(data)
        except Exception as e:
            result = f"An error occurred: {e}"
            logger.exception(e)

        await websocket.send_text(str(result))


@router.get("/flightgear-path")
def get_flightgear_path_hint():
    return {
        "path": get_flightgear_path(),
    }
