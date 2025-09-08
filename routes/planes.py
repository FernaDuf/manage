from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import conectar
from routes.eventos import registrar_evento

planes_bp = Blueprint("planes", __name__, url_prefix="/planes")

@planes_bp.route("/")
def listado():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, velocidad_subida, velocidad_bajada, precio FROM planes ORDER BY id")
    planes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("planes.html", planes=planes)

@planes_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo_plan():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        subida = request.form.get("velocidad_subida")
        bajada = request.form.get("velocidad_bajada")
        precio = request.form.get("precio")

        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO planes (nombre, velocidad_subida, velocidad_bajada, precio) VALUES (%s,%s,%s,%s)",
            (nombre, subida, bajada, precio),
        )
        conn.commit()
        cur.close()
        conn.close()

        registrar_evento("admin", f"Alta plan {nombre}", tipo="plan")
        flash("Plan creado con éxito", "success")
        return redirect(url_for("planes.listado"))

    return render_template("nuevo_plan.html")

@planes_bp.route("/editar/<int:plan_id>", methods=["GET", "POST"])
def editar_plan(plan_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, velocidad_subida, velocidad_bajada, precio FROM planes WHERE id=%s", (plan_id,))
    plan = cur.fetchone()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        subida = request.form.get("velocidad_subida")
        bajada = request.form.get("velocidad_bajada")
        precio = request.form.get("precio")

        cur.execute(
            "UPDATE planes SET nombre=%s, velocidad_subida=%s, velocidad_bajada=%s, precio=%s WHERE id=%s",
            (nombre, subida, bajada, precio, plan_id),
        )
        conn.commit()

        registrar_evento("admin", f"Edición plan {nombre}", tipo="plan")
        flash("Plan actualizado con éxito", "success")
        cur.close()
        conn.close()
        return redirect(url_for("planes.listado"))

    cur.close()
    conn.close()
    return render_template("editar_plan.html", plan=plan)

@planes_bp.route("/eliminar/<int:plan_id>", methods=["POST"])
def eliminar_plan(plan_id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nombre FROM planes WHERE id=%s", (plan_id,))
    plan = cur.fetchone()

    cur.execute("DELETE FROM planes WHERE id=%s", (plan_id,))
    conn.commit()
    cur.close()
    conn.close()

    if plan:
        registrar_evento("admin", f"Baja plan {plan[0]}", tipo="plan")
    flash("Plan eliminado", "warning")
    return redirect(url_for("planes.listado"))
