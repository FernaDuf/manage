import re

LOG_PATH = "/var/log/apache2/error.log"  # Cambiá si tu log está en otra ruta

# Expresiones para filtrar trazas de Python
TRACEBACK_START = re.compile(r"Traceback \(most recent call last\):")

def main():
    with open(LOG_PATH, "r") as f:
        lines = f.readlines()

    capture = False
    buffer = []
    for line in lines[-500:]:  # lee solo las últimas 500 líneas
        if TRACEBACK_START.search(line):
            capture = True
            buffer = [line.strip()]
        elif capture:
            buffer.append(line.strip())
            # Fin típico de error en Python/Flask/psycopg2
            if "Error" in line or "psycopg2" in line or "Exception" in line:
                print("\n--- ERROR DETECTADO ---")
                print("\n".join(buffer))
                print("-----------------------\n")
                capture = False

if __name__ == "__main__":
    main()
