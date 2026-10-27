import os
from sqlalchemy import URL, create_engine

database_url = URL.create(
    "postgresql+psycopg",
    username="learning",
    password=os.environ["POSTGRES_PASSWORD"],
    host="127.0.0.1",
    port=5432,
    database="learning"
)

engine = create_engine(database_url, connect_args={"connect_timeout": 5})
