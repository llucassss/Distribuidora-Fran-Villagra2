import sys
import os

#Agregar el directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta

class GestorPermisos:
    """Gestiona los permisos de los usuarios segun sus roles"""

    def __init__(self, usuario_id=None):
        self.usuario_id = usuario_id
        self.permisos_cache = {}

    def obtener_permisos_usuario(self, usuario_id=None):
        """Obtiene todos los permisos de usuario"""

