import os

import uvicorn
from loguru import logger

from flightgear_bridge.config import config
from flightgear_bridge.server import create_app

app = create_app(os.path.dirname(__file__))

if __name__ == "__main__":
    logger.info("Starting server")
    uvicorn.run(app, host=config.HTTP_HOST, port=config.HTTP_PORT, log_level="error")
