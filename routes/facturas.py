from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import conectar
from routes.eventos import registrar_evento
from datetime import datetime

facturas_bp = Blueprint("facturas", __name__, url_prefix="/facturas")

@facturas_bp.route("/")
def listado():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.fecha_emision, f.monto, f.tipo, f.estado, f.descripcion, c.nombre
        FROM facturas f
        LEFT JOIN clientes c ON f.cliente_id = c.id
        ORDER BY f.id DESC
    """)
    facturas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("facturas.listado.html", facturas=facturas)

@facturas_bp.route("/nueva", methods=["GET", "POST"])
def nueva_factura():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
    clientes = cur.fetchall()

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        monto = request.form.get("monto")
        tipo = request.form.get("tipo")
        estado = request.form.get("estado")
        descripcion = request.form.get("descripcion", "")

        fecha_emision = datetime.now().date()

        cur.execute(
            "INSERT INTO facturas (cliente_id, fecha_emision, tipo, monto, estado, descripcion) VALUES (%s,%s,%s,%s,%s,%s)",
            (cliente_id, fecha_emision, tipo, monto, estado, descripcion)
        )
        conn.commit()
        cur.close()
        conn.close()

        registrar_evento("admin", f"Nueva factura cliente {cliente_id}", tipo="factura", numero_cliente=cliente_id)
        flash("Factura creada con éxito", "success")
        return redirect(url_for("facturas.listado"))

    cur.close()
    conn.close()
    return render_template("nueva_factura.html", clientes=clientes)

@facturas_bp.route("/editar/<int:factura_id>", methods=["GET", "POST"])
def editar_factura(factura_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, cliente_id, fecha_emision, monto, tipo, estado, descripcion FROM facturas WHERE id=%s", (factura_id,))
    factura = cur.fetchone()

    cur.execute("SELECT id, nombre FROM clientes ORDER BY nombre")
    clientes = cur.fetchall()

    if request.method == "POST":
        monto = request.form.get("monto")
        tipo = request.form.get("tipo")
        estado = request.form.get("estado")
        descripcion = request.form.get("descripcion", "")
        cliente_id = request.form.get("cliente_id")

        cur.execute(
            "UPDATE facturas SET monto=%s, tipo=%s, estado=%s, descripcion=%s, cliente_id=%s WHERE id=%s",
            (monto, tipo, estado, descripcion, cliente_id, factura_id),
        )
        conn.commit()
        registrar_evento("admin", f"Edición factura ID {factura_id}", tipo="factura", numero_cliente=cliente_id)
        flash("Factura actualizada con éxito", "success")
        cur.close()
        conn.close()
        return redirect(url_for("facturas.listado"))

    cur.close()
    conn.close()
    return render_template("editar_factura.html", factura=factura, clientes=clientes)

@facturas_bp.route("/eliminar/<int:factura_id>", methods=["POST"])
def eliminar_factura(factura_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT cliente_id FROM facturas WHERE id=%s", (factura_id,))
    factura = cur.fetchone()

    cur.execute("DELETE FROM facturas WHERE id=%s", (factura_id,))
    conn.commit()
    cur.close()
    conn.close()

    if factura:
        registrar_evento("admin", f"Baja factura ID {factura_id}", tipo="factura", numero_cliente=factura[0])
    flash("Factura eliminada", "warning")
    return redirect(url_for("facturas.listado"))
