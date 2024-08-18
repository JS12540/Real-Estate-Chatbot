from pymongo.database import Database
from pymongo.mongo_client import MongoClient
import os
import atexit

class MongoDBClient:
    """Create a Singleton MongoDB client with a atexit db.close registered"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._client is None:
            self.client = MongoClient(os.getenv("MONGODB_CONNECTION_URI"))
            self.database = self.client[os.getenv("MONGODB_DATABASE_NAME")]

            atexit.register(self.close_connection)

    def get_client(self) -> MongoClient:
        """Get the MongoDB client
        Returns:
            MongoClient: Return the MongoDB client
        """
        return self.client

    def get_database(self) -> Database:
        """Get the MongoDB database on the env file database
        Returns:
            Database: The MongoDB database
        """
        return self.database

    def close_connection(self) -> None:
        """Registered handler for closing DB connection upon exit"""
        if self._client:
            self._client.close()
            self._client = None

    def signal_handler(self) -> None:
        """Callback registered on atexit"""
        self.close_connection()


# Connect at application startup
database = MongoDBClient().get_database()