from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import conectar
import hashlib
from functools import wraps

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("usuario"):
            flash("Debes iniciar sesión para acceder a esta página.", "warning")
            return redirect(url_for("usuarios.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("Acceso restringido. Se requiere rol administrador.", "danger")
            return redirect(url_for("clientes.listado"))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, usuario, password, rol FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session["usuario"] = user[1]
            session["rol"] = user[3]
            flash(f"Bienvenido {user[1]}!", "success")
            return redirect(url_for("clientes.listado"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")

@usuarios_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("usuarios.login"))

@usuarios_bp.route("/")
@admin_required
def listado():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, usuario, rol FROM usuarios ORDER BY id")
    usuarios = cur.fetchall()
    conn.close()
    return render_template("usuarios.html", usuarios=usuarios)

@usuarios_bp.route("/crear", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        rol = request.form["rol"]
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO usuarios (usuario, password, rol) VALUES (%s, %s, %s)", (usuario, password, rol))
        conn.commit()
        conn.close()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listado"))
    return render_template("crear_usuario.html")

@usuarios_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@admin_required
def editar(id):
    conn = conectar()
    cur = conn.cursor()

    if request.method == "POST":
        nuevo_usuario = request.form["usuario"]
        nuevo_rol = request.form["rol"]
        if nuevo_usuario == "admin":
            flash("No se puede editar el usuario admin.", "danger")
            return redirect(url_for("usuarios.listado"))
        cur.execute("UPDATE usuarios SET usuario=%s, rol=%s WHERE id=%s", (nuevo_usuario, nuevo_rol, id))
        conn.commit()
        conn.close()
        flash("Usuario modificado correctamente.", "success")
        return redirect(url_for("usuarios.listado"))

    cur.execute("SELECT id, usuario, rol FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()
    conn.close()

    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("usuarios.listado"))

    return render_template("editar_usuario.html", usuario=usuario)

@usuarios_bp.route("/eliminar/<int:id>")
@admin_required
def eliminar(id):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT usuario FROM usuarios WHERE id=%s", (id,))
    usuario = cur.fetchone()

    if usuario and usuario[0] != "admin":
        cur.execute("DELETE FROM usuarios WHERE id=%s", (id,))
        conn.commit()
        flash("Usuario eliminado correctamente.", "success")
    else:
        flash("No se puede eliminar el usuario admin.", "danger")

    conn.close()
    return redirect(url_for("usuarios.listado"))

@usuarios_bp.route("/cambiar_password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    mensaje = None
    if request.method == "POST":
        import hashlib
        actual = hashlib.sha256(request.form["actual"].encode()).hexdigest()
        nueva = hashlib.sha256(request.form["nueva"].encode()).hexdigest()
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM usuarios WHERE usuario=%s AND password=%s", (session["usuario"], actual))
        user = cur.fetchone()
        if user:
            cur.execute("UPDATE usuarios SET password=%s WHERE usuario=%s", (nueva, session["usuario"]))
            conn.commit()
            mensaje = "Contraseña actualizada correctamente."
        else:
            mensaje = "Contraseña actual incorrecta."
        conn.close()
    return render_template("cambiar_password.html", mensaje=mensaje)
