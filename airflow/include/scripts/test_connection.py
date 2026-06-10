from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv('DB_URL'))

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT version()'))
        print('Connection successful.')
        print(result.fetchone()[0])
except Exception as e:
    print(f'Connection failed: {e}')