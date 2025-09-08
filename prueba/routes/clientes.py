from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import conectar
from psycopg2.extras import RealDictCursor

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


# --- Helper para registrar eventos ---
def registrar_evento(usuario, tipo, descripcion, numero_cliente=None):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO eventos (usuario, tipo, descripcion, numero_cliente)
        VALUES (%s, %s, %s, %s)
    """, (usuario, tipo, descripcion, numero_cliente))
    conn.commit()
    cur.close()
    conn.close()


# --- Listado con filtros y búsqueda ---
@clientes_bp.route("/")
def listado():
    estado = request.args.get("estado", "activo")
    q = request.args.get("q", "").strip()

    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT c.*, p.nombre AS plan_nombre
        FROM clientes c
        LEFT JOIN planes p ON c.plan_id = p.id
        WHERE 1=1
    """
    params = []

    # Filtro estado
    if estado == "activo":
        query += " AND c.activo = true"
    elif estado == "inactivo":
        query += " AND c.activo = false"

    # Búsqueda
    if q:
        query += """
            AND (
                c.nombre ILIKE %s OR
                c.direccion ILIKE %s OR
                c.email ILIKE %s OR
                c.telefono ILIKE %s OR
                c.telefono2 ILIKE %s OR
                CAST(c.dni AS TEXT) ILIKE %s OR
                c.ip ILIKE %s
            )
        """
        for _ in range(7):
            params.append(f"%{q}%")

    query += " ORDER BY c.id DESC"

    cur.execute(query, params)
    clientes = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("listado.html", clientes=clientes, estado=estado, q=q)


# --- Crear nuevo cliente ---
@clientes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM planes ORDER BY nombre")
    planes = cur.fetchall()

    if request.method == "POST":
        activo = request.form.get("activo") == "on"

        cur.execute("""
            INSERT INTO clientes
                (nombre, direccion, entre_calles, dni, email, telefono, telefono2,
                 ip, plan_id, activo, gratis, bonificacion, bonificacion_meses, tipo_factura)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, numero_cliente
        """, (
            request.form["nombre"],
            request.form["direccion"],
            request.form.get("entre_calles"),
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form.get("telefono2"),
            request.form["ip"],
            request.form.get("plan_id"),
            activo,
            request.form.get("gratis", 0),
            request.form.get("bonificacion", 0),
            request.form.get("bonificacion_meses", 0),
            request.form.get("tipo_factura", "X"),
        ))
        nuevo = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        usuario = session.get("usuario", "sistema")
        registrar_evento(usuario, "CREAR CLIENTE", f"Se creó el cliente {request.form['nombre']}", numero_cliente=nuevo["numero_cliente"])

        flash("Cliente creado correctamente ✅", "success")
        return redirect(url_for("clientes.listado"))

    cur.close()
    conn.close()
    return render_template("alta.html", planes=planes)


# --- Editar cliente ---
@clientes_bp.route("/editar/<int:cliente_id>", methods=["GET", "POST"])
def editar(cliente_id):
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM planes ORDER BY nombre")
    planes = cur.fetchall()

    if request.method == "POST":
        activo = request.form.get("activo") == "on"

        cur.execute("""
            UPDATE clientes
               SET nombre=%s,
                   direccion=%s,
                   entre_calles=%s,
                   dni=%s,
                   email=%s,
                   telefono=%s,
                   telefono2=%s,
                   ip=%s,
                   plan_id=%s,
                   activo=%s,
                   gratis=%s,
                   bonificacion=%s,
                   bonificacion_meses=%s,
                   tipo_factura=%s
             WHERE id=%s
        """, (
            request.form["nombre"],
            request.form["direccion"],
            request.form.get("entre_calles"),
            request.form["dni"],
            request.form["email"],
            request.form["telefono"],
            request.form.get("telefono2"),
            request.form["ip"],
            request.form.get("plan_id"),
            activo,
            request.form.get("gratis", 0),
            request.form.get("bonificacion", 0),
            request.form.get("bonificacion_meses", 0),
            request.form.get("tipo_factura", "X"),
            cliente_id
        ))
        conn.commit()
        cur.close()
        conn.close()

        usuario = session.get("usuario", "sistema")
        registrar_evento(usuario, "EDITAR CLIENTE", f"Se editó el cliente ID {cliente_id}", numero_cliente=cliente_id)

        flash("Cliente actualizado correctamente ✅", "success")
        return redirect(url_for("clientes.listado"))

    # GET
    cur.execute("SELECT * FROM clientes WHERE id=%s", (cliente_id,))
    cliente = cur.fetchone()
    cur.close()
    conn.close()

    if not cliente:
        flash("Cliente no encontrado", "warning")
        return redirect(url_for("clientes.listado"))

    return render_template("editar.html", cliente=cliente, planes=planes)


# --- Eliminar cliente ---
@clientes_bp.route("/eliminar/<int:cliente_id>", methods=["POST"])
def eliminar(cliente_id):
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("DELETE FROM clientes WHERE id=%s RETURNING numero_cliente", (cliente_id,))
    eliminado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    usuario = session.get("usuario", "sistema")
    if eliminado:
        registrar_evento(usuario, "ELIMINAR CLIENTE", f"Se eliminó el cliente ID {cliente_id}", numero_cliente=eliminado["numero_cliente"])

    flash("Cliente eliminado ❌", "success")
    return redirect(url_for("clientes.listado"))
