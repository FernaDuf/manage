from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import conectar
from routes.usuarios import login_required
import psycopg2.extras

facturas_bp = Blueprint("facturas", __name__, url_prefix="/facturas")


@facturas_bp.route("/")
@login_required
def listado():
    """Lista todas las facturas creadas"""
    conn = conectar()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT f.id,
               f.fecha_emision,
               f.tipo,
               f.monto,
               f.estado,
               f.descripcion,
               c.nombre AS cliente
        FROM facturas f
        JOIN clientes c ON f.cliente_id = c.id
        ORDER BY f.fecha_emision DESC
    """)
    facturas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("facturas/listado.html", facturas=facturas)


@facturas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    """Crear nueva factura manualmente"""
    conn = conectar()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        tipo = request.form.get("tipo")
        monto = request.form.get("monto")
        estado = request.form.get("estado")
        descripcion = request.form.get("descripcion")

        cur.execute("""
            INSERT INTO facturas (cliente_id, fecha_emision, tipo, monto, estado, descripcion)
            VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
        """, (cliente_id, tipo, monto, estado, descripcion))
        conn.commit()
        cur.close()
        conn.close()
        flash("Factura creada correctamente", "success")
        return redirect(url_for("facturas.listado"))

    # Para renderizar el formulario necesito la lista de clientes
    cur.execute("SELECT id, nombre FROM clientes ORDER BY nombre ASC")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("facturas/nueva.html", clientes=clientes)


@facturas_bp.route("/pago/<int:id>", methods=["POST"])
@login_required
def registrar_pago(id):
    """Marcar una factura como pagada"""
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE facturas SET estado = %s WHERE id = %s", ("Pagada", id))
    conn.commit()
    cur.close()
    conn.close()
    flash("Factura marcada como pagada", "success")
    return redirect(url_for("facturas.listado"))


@facturas_bp.route("/manual")
@login_required
def manual():
    """Vista placeholder para facturación manual"""
    return render_template("facturas/manual.html")


@facturas_bp.route("/mensual")
@login_required
def mensual():
    """Vista placeholder para facturación mensual"""
    return render_template("facturas/mensual.html")
