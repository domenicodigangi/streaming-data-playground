import logging

from simulator.core.publishers.abstract_publisher import (
    AbstractPeriodicMsgPublisher,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogsPublisher(AbstractPeriodicMsgPublisher):
    def __init__(self):
        super().__init__()
        self.logger = logger

    def publish_one(self, msg: bytes):
        self.logger.info(msg)
