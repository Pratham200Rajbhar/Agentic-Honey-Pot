"""
Database connection management
"""

from prisma import Prisma
import logging

logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._client = Prisma()
        return cls._instance

    @property
    def client(self) -> Prisma:
        return self._client

    async def connect(self):
        if not self._client.is_connected():
            logger.info("Connecting to database...")
            await self._client.connect()
            logger.info("Database connected.")

    async def disconnect(self):
        if self._client.is_connected():
            logger.info("Disconnecting from database...")
            await self._client.disconnect()
            logger.info("Database disconnected.")


db = Database()
