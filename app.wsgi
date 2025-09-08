import sys
import logging
import os
import site

logging.basicConfig(stream=sys.stderr)

# Ruta del proyecto
project_home = '/home/fer/Manage'
if project_home not in sys.path:
    sys.path.insert(0, '/home/fer/Manage')

# Activar entorno virtual
venv_path = '/home/fer/Manage/venv/lib/python3.11/site-packages'
site.addsitedir(venv_path)

# Importar la aplicación Flask
from app import app as application
