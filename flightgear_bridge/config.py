import os

from pydantic import BaseSettings


class Config(BaseSettings):
    LOGS_DIR: str = "logs"
    HTTP_HOST: str = "127.0.0.1"
    HTTP_PORT: int = 8000

    FLIGHT_GEAR_TELNET_HOST: str = "localhost"
    FLIGHT_GEAR_TELNET_PORT: int = 5555
    FLIGHT_GEAR_TELNET_POLLING_INTERVAL: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        os.makedirs(self.LOGS_DIR, exist_ok=True)


config = Config()
