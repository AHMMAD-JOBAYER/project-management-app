import os
import mysql.connector
from abc import ABC, abstractmethod
import dotenv
from pathlib import Path

from pydantic import EmailStr

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR / ".env")


class DataBase(ABC):
    def __init__(self, driver) -> None:
        self.driver = driver

    @abstractmethod
    def connect_to_database(self):
        raise NotImplementedError()

    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor(dictionary=True)
        return self

    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()


class MySQLDatabase(DataBase):
    def __init__(self) -> None:
        self.driver = mysql.connector
        super().__init__(self.driver)

    def connect_to_database(self):
        return self.driver.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )


if __name__ == "__main__":
    pass
