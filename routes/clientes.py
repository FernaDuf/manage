from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import conectar
from routes.eventos import registrar_evento

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@clientes_bp.route("/")
def listado():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.numero_cliente, c.nombre, c.dni, c.direccion, c.email, c.ip, c.activo, p.nombre
        FROM clientes c
        LEFT JOIN planes p ON c.plan_id = p.id
        ORDER BY c.id
    """)
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("listado.html", clientes=clientes)

@clientes_bp.route("/alta", methods=["GET", "POST"])
def alta():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM planes ORDER BY nombre")
    planes = cur.fetchall()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        dni = request.form.get("dni")
        direccion = request.form.get("direccion")
        email = request.form.get("email")
        ip = request.form.get("ip")
        plan_id = request.form.get("plan_id") or None
        activo = True if request.form.get("activo") else False

        cur.execute("""
            INSERT INTO clientes (nombre, dni, direccion, email, ip, plan_id, activo)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (nombre, dni, direccion, email, ip, plan_id, activo))
        conn.commit()

        registrar_evento("admin", f"Alta cliente {nombre}", tipo="cliente")
        flash("Cliente creado con éxito", "success")
        cur.close()
        conn.close()
        return redirect(url_for("clientes.listado"))

    cur.close()
    conn.close()
    return render_template("alta.html", planes=planes)

@clientes_bp.route("/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar(cliente_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, numero_cliente, nombre, dni, direccion, email, ip, plan_id, activo FROM clientes WHERE id=%s", (cliente_id,))
    cliente = cur.fetchone()

    cur.execute("SELECT id, nombre FROM planes ORDER BY nombre")
    planes = cur.fetchall()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        dni = request.form.get("dni")
        direccion = request.form.get("direccion")
        email = request.form.get("email")
        ip = request.form.get("ip")
        plan_id = request.form.get("plan_id") or None
        activo = True if request.form.get("activo") else False

        cur.execute("""
            UPDATE clientes
            SET nombre=%s, dni=%s, direccion=%s, email=%s, ip=%s, plan_id=%s, activo=%s
            WHERE id=%s
        """, (nombre, dni, direccion, email, ip, plan_id, activo, cliente_id))
        conn.commit()

        registrar_evento("admin", f"Edición cliente {nombre}", tipo="cliente", numero_cliente=cliente_id)
        flash("Cliente actualizado con éxito", "success")
        cur.close()
        conn.close()
        return redirect(url_for("clientes.listado"))

    cur.close()
    conn.close()
    return render_template("editar.html", cliente=cliente, planes=planes)

@clientes_bp.route("/eliminar/<int:cliente_id>", methods=["POST"])
def eliminar(cliente_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM clientes WHERE id=%s", (cliente_id,))
    cliente = cur.fetchone()

    cur.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
    conn.commit()
    cur.close()
    conn.close()

    if cliente:
        registrar_evento("admin", f"Baja cliente {cliente[0]}", tipo="cliente", numero_cliente=cliente_id)
    flash("Cliente eliminado", "warning")
    return redirect(url_for("clientes.listado"))
