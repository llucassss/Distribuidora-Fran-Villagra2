from kivy.uix.boxlayout import BoxLayout
import sys
import os
import hashlib

# Importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta

class LoginScreen(BoxLayout):
    """Pantalla de login"""

    def validar_login(self, usuario, password):
        """Validar credenciales del usuario"""
        if not usuario or not password:
            self.mostrar_mensaje("Por favor, complete todos los campos", error=True)
            return False

        # Generar hash de contraseña
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Consultar BD
        consulta = """
            SELECT u.UsuarioID, u.NombreUsuario, u.RolID, r.Nombre as RolNombre, u.EmpleadoID
            FROM Usuarios u
            INNER JOIN Roles r ON u.RolID = r.RolID
            WHERE u.NombreUsuario = ? AND u.ClaveHash = ? AND u.Estado = 1
        """
        resultado = ejecutar_consulta(consulta, (usuario, password_hash))

        if resultado and len(resultado) > 0:
            usuario_data = {
                'UsuarioID': resultado[0][0],
                'NombreUsuario': resultado[0][1],
                'RolID': resultado[0][2],
                'RolNombre': resultado[0][3],
                'EmpleadoID': resultado[0][4]
            }

            self.mostrar_mensaje(f"¡Bienvenido {usuario_data['NombreUsuario']}!", error=False)
            print(f"Usuario autenticado: {usuario_data}")
            return True
        else:
            self.mostrar_mensaje("Usuario o contraseña incorrectos", error=True)
            return False

    def mostrar_mensaje(self, mensaje, error=True):
        """Muestra un mensaje en la interfaz"""
        if hasattr(self, 'ids') and 'mensaje_label' in self.ids:
            mensaje_label = self.ids.mensaje_label
            mensaje_label.text = mensaje
            if error:
                mensaje_label.color = (1, 0, 0, 1)  # Rojo
            else:
                mensaje_label.color = (0, 1, 0, 1)  # Verde

