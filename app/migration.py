from database import MySQLDatabase


migration_table = {
    "user": """
        create table user(
        sid int primary key AUTO_INCREMENT,
        email varchar(255) unique,
        firstname varchar(255),
        lastname varchar(255),
        password varchar(255)
        )
        """,
}

if __name__ == "__main__":
    with MySQLDatabase() as db:
        db.cursor.execute(migration_table["user"])
