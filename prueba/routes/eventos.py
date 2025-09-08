from flask import Blueprint, render_template, request, send_file, current_app
from db import conectar
from datetime import datetime
import csv, io

eventos_bp = Blueprint("eventos", __name__, url_prefix="/eventos")

def registrar_evento(usuario, descripcion, tipo="sistema", numero_cliente=None):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO eventos (usuario, descripcion, tipo, numero_cliente, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario or '-', descripcion or '-', tipo or 'sistema', numero_cliente, datetime.now())
        )
        conn.commit()
    except Exception as e:
        try:
            current_app.logger.exception("registrar_evento failed: %s", e)
        except Exception:
            print("registrar_evento failed:", e)
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass

@eventos_bp.route("/")
def listado():
    tipo = request.args.get("tipo")
    numero_cliente = request.args.get("numero_cliente")
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")

    conn = conectar()
    cur = conn.cursor()
    query = "SELECT id, usuario, descripcion, tipo, numero_cliente, fecha FROM eventos WHERE 1=1"
    params = []
    if tipo:
        query += " AND tipo = %s"
        params.append(tipo)
    if numero_cliente:
        query += " AND numero_cliente = %s"
        params.append(numero_cliente)
    if fecha_inicio and fecha_fin:
        query += " AND fecha BETWEEN %s AND %s"
        params.append(fecha_inicio)
        params.append(fecha_fin)
    query += " ORDER BY fecha DESC"
    cur.execute(query, tuple(params))
    eventos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("eventos.html", eventos=eventos)

@eventos_bp.route("/descargar")
def descargar_eventos():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")

    conn = conectar()
    cur = conn.cursor()
    query = "SELECT id, usuario, descripcion, tipo, numero_cliente, fecha FROM eventos WHERE 1=1"
    params = []
    if fecha_inicio and fecha_fin:
        query += " AND fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    query += " ORDER BY fecha DESC"
    cur.execute(query, tuple(params))
    eventos = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Usuario", "Descripción", "Tipo", "Número Cliente", "Fecha"])
    for e in eventos:
        writer.writerow([e[0], e[1], e[2], e[3], e[4], e[5].strftime("%Y-%m-%d %H:%M:%S") if e[5] else ""])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8")), mimetype="text/csv", as_attachment=True,
                     download_name=f"eventos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
