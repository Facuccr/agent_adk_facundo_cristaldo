import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "negocio.db")

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM productos")
    if cursor.fetchone()[0] == 0:
        productos_iniciales = [
            ("Teclado Mecánico Kumara K552", "Periféricos", 55000.0, 12),
            ("Mouse Gamer Cobra M711", "Periféricos", 32000.0, 20),
            ("Monitor IPS 24 pulgadas 144Hz", "Monitores", 240000.0, 4),
            ("Placa de Video RTX 4050", "Hardware", 650000.0, 2),
            ("Memoria RAM DDR4 16GB", "Hardware", 48000.0, 0),
        ]
        cursor.executemany(
            "INSERT INTO productos (nombre, categoria, precio, stock) VALUES (?, ?, ?, ?)",
            productos_iniciales
        )

        ventas_iniciales = [
            (1, 3, 165000.0, "2026-11-10"),
            (2, 5, 160000.0, "2026-11-12"),
            (3, 2, 480000.0, "2026-11-15"),
            (4, 1, 650000.0, "2026-11-18"),
        ]
        cursor.executemany(
            "INSERT INTO ventas (producto_id, cantidad, total, fecha) VALUES (?, ?, ?, ?)",
            ventas_iniciales
        )

    conn.commit()
    conn.close()

inicializar_db()