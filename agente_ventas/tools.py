import sqlite3
from ddgs import DDGS
from .database import DB_PATH


def consultar_stock(termino_busqueda: str) -> dict:
    """
    Consulta el inventario de productos por nombre o categoría en la base de datos.

    Args:
        termino_busqueda (str): Nombre parcial del producto o categoría a buscar (ej. 'Teclado', 'Hardware').

    Returns:
        dict: Estado de la consulta y lista de productos encontrados con su precio y stock.
    """
    if not termino_busqueda or not isinstance(termino_busqueda, str) or len(termino_busqueda.strip()) < 2:
        return {
            "status": "error",
            "mensaje": "Argumento inválido: debés ingresar al menos 2 caracteres para buscar un producto o categoría."
        }

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        patron = f"%{termino_busqueda.strip()}%"
        cursor.execute(
            "SELECT id, nombre, categoria, precio, stock FROM productos WHERE nombre LIKE ? OR categoria LIKE ?",
            (patron, patron)
        )
        filas = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not filas:
            return {
                "status": "vacio",
                "mensaje": f"No se encontraron productos que coincidan con '{termino_busqueda}'."
            }

        return {"status": "ok", "productos": filas}

    except Exception as e:
        return {"status": "error", "mensaje": f"Error al consultar la base de datos: {str(e)}"}


def registrar_venta(producto_id: int, cantidad: int) -> dict:
    """
    Registra una nueva venta en el sistema y descuenta automáticamente el stock disponible.

    Args:
        producto_id (int): ID numérico exacto del producto en el inventario.
        cantidad (int): Cantidad de unidades vendidas (debe ser mayor a 0).

    Returns:
        dict: Confirmación de la venta con el monto total calculado o mensaje de error.
    """
    if not isinstance(producto_id, int) or producto_id <= 0:
        return {"status": "error", "mensaje": "El ID del producto debe ser un número entero positivo."}

    if not isinstance(cantidad, int) or cantidad <= 0:
        return {"status": "error", "mensaje": "La cantidad a vender debe ser un número entero mayor a cero."}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT nombre, precio, stock FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()

        if not producto:
            conn.close()
            return {"status": "vacio", "mensaje": f"No existe ningún producto con ID {producto_id}."}

        nombre, precio, stock_actual = producto

        if stock_actual < cantidad:
            conn.close()
            return {
                "status": "error",
                "mensaje": f"Stock insuficiente para '{nombre}'. Disponible: {stock_actual}, solicitado: {cantidad}."
            }

        total_venta = precio * cantidad
        nuevo_stock = stock_actual - cantidad

        cursor.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))
        cursor.execute(
            "INSERT INTO ventas (producto_id, cantidad, total, fecha) VALUES (?, ?, ?, date('now'))",
            (producto_id, cantidad, total_venta)
        )

        conn.commit()
        conn.close()

        return {
            "status": "ok",
            "mensaje": f"Venta registrada: {cantidad}x {nombre}. Total: ${total_venta:,.2f}. Stock restante: {nuevo_stock}."
        }

    except Exception as e:
        return {"status": "error", "mensaje": f"Error interno al registrar la venta: {str(e)}"}


def obtener_resumen_ventas(categoria: str = "TODAS") -> dict:
    """
    Calcula métricas financieras de facturación total y unidades vendidas, filtrando opcionalmente por categoría.

    Args:
        categoria (str): Categoría específica a analizar (ej. 'Hardware', 'Periféricos') o 'TODAS' para el total general.

    Returns:
        dict: Resumen con cantidad de operaciones, unidades vendidas y facturación acumulada.
    """
    if not categoria or not isinstance(categoria, str):
        categoria = "TODAS"

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if categoria.strip().upper() == "TODAS":
            cursor.execute("""
                SELECT COUNT(v.id), COALESCE(SUM(v.cantidad), 0), COALESCE(SUM(v.total), 0)
                FROM ventas v
            """)
        else:
            cursor.execute("""
                SELECT COUNT(v.id), COALESCE(SUM(v.cantidad), 0), COALESCE(SUM(v.total), 0)
                FROM ventas v
                JOIN productos p ON v.producto_id = p.id
                WHERE LOWER(p.categoria) = LOWER(?)
            """, (categoria.strip(),))

        operaciones, unidades, facturacion = cursor.fetchone()
        conn.close()

        if operaciones == 0:
            return {
                "status": "vacio",
                "mensaje": f"No se registran ventas para la categoría '{categoria}'."
            }

        return {
            "status": "ok",
            "categoria": categoria,
            "operaciones_realizadas": operaciones,
            "unidades_vendidas": unidades,
            "facturacion_total": facturacion
        }

    except Exception as e:
        return {"status": "error", "mensaje": f"Error al calcular métricas de ventas: {str(e)}"}


def buscar_precio_referencia_web(producto: str, max_results: int = 3) -> dict:
    """
    Busca precios de referencia o especificaciones de un producto tecnológico en internet mediante DuckDuckGo.

    Args:
        producto (str): Nombre del producto a consultar en la web.
        max_results (int): Cantidad máxima de resultados a devolver (entre 1 y 5).

    Returns:
        dict: Resultados de búsqueda obtenidos de internet.
    """
    if not producto or len(producto.strip()) < 3:
        return {"status": "error", "mensaje": "Debés especificar un nombre de producto válido para buscar en la web."}

    max_results = max(1, min(int(max_results), 5))

    try:
        query = f"{producto.strip()} precio Argentina"
        resultados = DDGS().text(query=query, max_results=max_results)

        if not resultados:
            return {"status": "vacio", "mensaje": f"No se encontraron resultados web para '{producto}'."}

        return {"status": "ok", "resultados": resultados}

    except Exception as e:
        return {"status": "error", "mensaje": f"Fallo en la búsqueda externa: {str(e)}"}