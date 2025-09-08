from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import conectar
from psycopg2.extras import RealDictCursor

planes_bp = Blueprint("planes", __name__, url_prefix="/planes")

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

# --- Rutas de planes ---
@planes_bp.route("/")
def listado():
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM planes ORDER BY id DESC")
    planes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("planes_listado.html", planes=planes)

@planes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    conn = conectar()
    cur = conn.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO planes (nombre, velocidad_bajada, velocidad_subida, precio)
            VALUES (%s, %s, %s, %s)
        """, (
            request.form["nombre"],
            request.form["velocidad_bajada"],
            request.form["velocidad_subida"],
            request.form["precio"]
        ))
        conn.commit()
        cur.close()
        conn.close()

        # Registrar evento
        usuario = session.get("usuario", "sistema")
        registrar_evento(usuario, "CREAR PLAN", f"Se creó el plan {request.form['nombre']}")

        flash("Plan creado correctamente ✅", "success")
        return redirect(url_for("planes.listado"))

    cur.close()
    conn.close()
    return render_template("planes_alta.html")

@planes_bp.route("/editar/<int:plan_id>", methods=["GET", "POST"])
def editar(plan_id):
    conn = conectar()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if request.method == "POST":
        cur.execute("""
            UPDATE planes
               SET nombre=%s,
                   velocidad_bajada=%s,
                   velocidad_subida=%s,
                   precio=%s
             WHERE id=%s
        """, (
            request.form["nombre"],
            request.form["velocidad_bajada"],
            request.form["velocidad_subida"],
            request.form["precio"],
            plan_id
        ))
        conn.commit()
        cur.close()
        conn.close()

        usuario = session.get("usuario", "sistema")
        registrar_evento(usuario, "EDITAR PLAN", f"Se editó el plan ID {plan_id}")

        flash("Plan actualizado correctamente ✅", "success")
        return redirect(url_for("planes.listado"))

    cur.execute("SELECT * FROM planes WHERE id=%s", (plan_id,))
    plan = cur.fetchone()
    cur.close()
    conn.close()

    if not plan:
        flash("Plan no encontrado", "warning")
        return redirect(url_for("planes.listado"))

    return render_template("planes_editar.html", plan=plan)

@planes_bp.route("/eliminar/<int:plan_id>", methods=["POST"])
def eliminar(plan_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM planes WHERE id=%s", (plan_id,))
    conn.commit()
    cur.close()
    conn.close()

    usuario = session.get("usuario", "sistema")
    registrar_evento(usuario, "ELIMINAR PLAN", f"Se eliminó el plan ID {plan_id}")

    flash("Plan eliminado ❌", "success")
    return redirect(url_for("planes.listado"))
