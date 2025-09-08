import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "clientesdb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))

MT_HOST = os.getenv("MT_HOST", "192.168.88.1")
MT_SSH_PORT = int(os.getenv("MT_SSH_PORT", "22"))
MT_USER = os.getenv("MT_USER", "admin")
MT_PASSWORD = os.getenv("MT_PASSWORD", "")
MT_BLOCK_LIST = os.getenv("MT_BLOCK_LIST", "BLOQUEADOS")
MT_QUEUE_PREFIX = os.getenv("MT_QUEUE_PREFIX", "Q")
MT_QUEUE_PARENT = os.getenv("MT_QUEUE_PARENT", "")