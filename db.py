import psycopg2
import hashlib
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

def conectar():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS planes (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(80) UNIQUE NOT NULL,
        bajada_kbps INTEGER NOT NULL,
        subida_kbps INTEGER NOT NULL,
        precio NUMERIC(12,2) NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id SERIAL PRIMARY KEY,
        numero_cliente INTEGER UNIQUE NOT NULL,
        nombre VARCHAR(120) NOT NULL,
        dni VARCHAR(32),
        direccion VARCHAR(200),
        email VARCHAR(120),
        ip INET NOT NULL,
        activo BOOLEAN NOT NULL DEFAULT TRUE,
        plan_id INTEGER REFERENCES planes(id) ON DELETE SET NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id SERIAL PRIMARY KEY,
        cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
        periodo VARCHAR(20) NOT NULL,
        monto NUMERIC(12,2) NOT NULL,
        pagada BOOLEAN NOT NULL DEFAULT FALSE,
        fecha_emision TIMESTAMP DEFAULT NOW(),
        fecha_pago TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(80),
        descripcion TEXT NOT NULL,
        tipo VARCHAR(40),
        numero_cliente INTEGER,
        creado TIMESTAMP DEFAULT NOW()
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(80) UNIQUE NOT NULL,
        password VARCHAR(128) NOT NULL,
        rol VARCHAR(40) NOT NULL DEFAULT 'usuario'
    )
    """)

    cur.execute("SELECT 1 FROM usuarios WHERE usuario=%s", ('admin',))
    if not cur.fetchone():
        pw_hash = hashlib.sha256('admin'.encode()).hexdigest()
        cur.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)", ('admin', pw_hash, 'admin'))

    conn.commit()
    conn.close()