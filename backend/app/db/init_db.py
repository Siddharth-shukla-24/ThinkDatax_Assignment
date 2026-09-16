from app.db import models   
from app.db.database import Base, engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables created.")


if __name__ == "__main__":
    init_db()