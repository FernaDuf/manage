from flask import Flask, redirect, url_for
from config import SECRET_KEY
from routes.clientes import clientes_bp
from routes.planes import planes_bp
from routes.facturas import facturas_bp
from routes.eventos import eventos_bp
try:
    from routes.usuarios import usuarios_bp
except Exception:
    usuarios_bp = None

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    app.register_blueprint(clientes_bp)
    app.register_blueprint(planes_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(eventos_bp)
    if usuarios_bp:
        app.register_blueprint(usuarios_bp)

    @app.route("/")
    def index():
        return redirect(url_for("clientes.listado"))

    @app.errorhandler(404)
    def not_found(e):
        return ("Página no encontrada", 404)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)