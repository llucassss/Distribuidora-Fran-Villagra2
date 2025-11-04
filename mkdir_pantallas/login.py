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
            # Diagnóstico: verificar si el usuario existe
            self.diagnosticar_usuario(usuario, password_hash)
            self.mostrar_mensaje("Usuario o contraseña incorrectos", error=True)
            return False

    def diagnosticar_usuario(self, usuario, password_hash):
        """Diagnostica por qué falló el login"""
        # Verificar si el usuario existe
        consulta_usuario = "SELECT UsuarioID, NombreUsuario, Estado, ClaveHash FROM Usuarios WHERE NombreUsuario = ?"
        resultado_usuario = ejecutar_consulta(consulta_usuario, (usuario,))
        
        if not resultado_usuario or len(resultado_usuario) == 0:
            print(f"❌ Error: El usuario '{usuario}' no existe en la base de datos")
            print("💡 Solución: Ejecuta 'python mkdir_database/permisos.py' para crear los usuarios")
            return
        
        usuario_db = resultado_usuario[0]
        usuario_id = usuario_db[0]
        nombre_usuario = usuario_db[1]
        estado = usuario_db[2]
        hash_db = usuario_db[3]
        
        print(f"🔍 Diagnóstico para usuario: {nombre_usuario}")
        
        # Verificar estado
        if estado == 0:
            print(f"❌ Error: El usuario '{usuario}' está inactivo (Estado = 0)")
            print("💡 Solución: Activa el usuario en la base de datos")
        
        # Verificar hash
        if hash_db != password_hash:
            print(f"❌ Error: La contraseña no coincide")
            print(f"   Hash en BD: {hash_db[:20]}...")
            print(f"   Hash ingresado: {password_hash[:20]}...")
            print("💡 Solución: Verifica que la contraseña sea correcta")
        
        # Verificar rol
        consulta_rol = """
            SELECT r.Nombre FROM Usuarios u
            INNER JOIN Roles r ON u.RolID = r.RolID
            WHERE u.UsuarioID = ?
        """
        resultado_rol = ejecutar_consulta(consulta_rol, (usuario_id,))
        
        if resultado_rol:
            print(f"✅ Rol asignado: {resultado_rol[0][0]}")
        else:
            print(f"❌ Error: El usuario no tiene un rol asignado")

    def mostrar_mensaje(self, mensaje, error=True):
        """Muestra un mensaje en la interfaz"""
        if hasattr(self, 'ids') and 'mensaje_label' in self.ids:
            mensaje_label = self.ids.mensaje_label
            mensaje_label.text = mensaje
            if error:
                mensaje_label.color = (1, 0, 0, 1)  # Rojo
            else:
                mensaje_label.color = (0, 1, 0, 1)  # Verde

