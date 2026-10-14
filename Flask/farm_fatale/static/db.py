from sqlalchemy import create_engine
from static.config import DATABASE_URL

engine = create_engine(DATABASE_URL)