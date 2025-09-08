from datetime import date
import psycopg2

def generar_facturas_mensuales():
    conn = psycopg2.connect(
        host="localhost",
        database="clientesdb",
        user="feroperador",
        password="casatecnico25"
    )
    c = conn.cursor()

    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)

    c.execute("SELECT id, plan_id FROM clientes WHERE activo = 1 AND plan_id IS NOT NULL")
    clientes = c.fetchall()

    for cliente_id, plan_id in clientes:
        c.execute("SELECT velocidad_subida, velocidad_bajada FROM planes WHERE id=%s", (plan_id,))
        plan = c.fetchone()
        if not plan:
            continue
        velocidad_subida, velocidad_bajada = plan
        monto = (velocidad_subida + velocidad_bajada) * 10  # Ajustar tarifa

        c.execute("""
            INSERT INTO facturas (cliente_id, fecha_emision, tipo, monto, estado, descripcion)
            VALUES (%s, %s, %s, %s, 'pendiente', %s)
        """, (cliente_id, primer_dia, 'factura', monto, f'Factura mensual plan {plan_id}'))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    generar_facturas_mensuales()