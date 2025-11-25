import database as db
import datetime as dt

def pedidos_por_semana(idempleado):
    """Return number of orders per week for a given employee ID."""
    query = """
        SELECT DATEPART(WEEK, fecha) AS semana, COUNT(*) AS total_pedidos
        FROM pedidos
        WHERE idempleado = %s
        GROUP BY DATEPART(WEEK, fecha)
        ORDER BY semana;
    """
    results = db.read_data(query, (idempleado,))
    return results