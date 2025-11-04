import sys
import os
import hashlib

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mkdir_database.conexion import ejecutar_consulta, conectar, cerrar_conexion

class GestorPermisos:
    """Gestiona los permisos de los usuarios según sus roles"""

    def __init__(self, usuario_id=None):
        self.usuario_id = usuario_id
        self.permisos_cache = {}

    def obtener_permisos_usuario(self, usuario_id=None):
        """Obtiene todos los permisos de un usuario basado en su rol"""
        if usuario_id is None:
            usuario_id = self.usuario_id
        
        if not usuario_id:
            return []
        
        # Verificar cache
        if usuario_id in self.permisos_cache:
            return self.permisos_cache[usuario_id]
        
        consulta = """
            SELECT DISTINCT p.Nombre, p.Descripcion, p.Modulo
            FROM Permisos p
            INNER JOIN RolPermisos rp ON p.PermisoID = rp.PermisoID
            INNER JOIN Roles r ON rp.RolID = r.RolID
            INNER JOIN Usuarios u ON u.RolID = r.RolID
            WHERE u.UsuarioID = ? AND u.Estado = 1
        """
        
        resultado = ejecutar_consulta(consulta, (usuario_id,))
        
        permisos = []
        if resultado:
            permisos = [{'nombre': row[0], 'descripcion': row[1], 'modulo': row[2]} 
                       for row in resultado]
        
        # Guardar en cache
        self.permisos_cache[usuario_id] = permisos
        return permisos

    def tiene_permiso(self, nombre_permiso, usuario_id=None):
        """Verifica si un usuario tiene un permiso específico"""
        permisos = self.obtener_permisos_usuario(usuario_id)
        nombres_permisos = [p['nombre'] for p in permisos]
        return nombre_permiso in nombres_permisos

    def tiene_permiso_modulo(self, modulo, accion='ver', usuario_id=None):
        """Verifica si un usuario tiene permiso para una acción en un módulo"""
        nombre_permiso = f"{accion}_{modulo}"
        return self.tiene_permiso(nombre_permiso, usuario_id)

    def obtener_permisos_modulo(self, modulo, usuario_id=None):
        """Obtiene todos los permisos de un módulo específico para un usuario"""
        permisos = self.obtener_permisos_usuario(usuario_id)
        return [p for p in permisos if p['modulo'] == modulo]

    def es_admin(self, usuario_id=None):
        """Verifica si un usuario es administrador"""
        if usuario_id is None:
            usuario_id = self.usuario_id
        
        if not usuario_id:
            return False
        
        consulta = """
            SELECT r.Nombre
            FROM Usuarios u
            INNER JOIN Roles r ON u.RolID = r.RolID
            WHERE u.UsuarioID = ? AND r.Nombre = 'Administrador'
        """
        
        resultado = ejecutar_consulta(consulta, (usuario_id,))
        return resultado is not None and len(resultado) > 0

    def limpiar_cache(self):
        """Limpia la caché de permisos"""
        self.permisos_cache = {}


# ======================================
# FUNCIONES PARA CREAR USUARIO ADMIN
# ======================================

def hash_password(password):
    """Genera hash SHA256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

def crear_rol_administrador():
    """Crea el rol Administrador si no existe"""
    conexion = conectar()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor()
        
        # Verificar si el rol existe
        cursor.execute("SELECT RolID FROM Roles WHERE Nombre = 'Administrador'")
        resultado = cursor.fetchone()
        
        if resultado:
            rol_id = resultado[0]
            print("Rol Administrador ya existe")
            return rol_id
        
        # Crear el rol
        cursor.execute("INSERT INTO Roles (Nombre) VALUES ('Administrador')")
        cursor.execute("SELECT SCOPE_IDENTITY()")
        rol_id = int(cursor.fetchone()[0])
        conexion.commit()
        
        print(f"Rol Administrador creado (ID: {rol_id})")
        return rol_id
    except Exception as error:
        print(f"Error al crear rol Administrador: {error}")
        conexion.rollback()
        return None
    finally:
        cerrar_conexion(conexion)

def asignar_todos_permisos_administrador(rol_id):
    """Asigna todos los permisos al rol Administrador"""
    conexion = conectar()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        # Obtener todos los permisos
        cursor.execute("SELECT PermisoID FROM Permisos")
        permisos = cursor.fetchall()
        
        if not permisos:
            print("No hay permisos en la base de datos. Creando permisos básicos...")
            crear_permisos_basicos()
            cursor.execute("SELECT PermisoID FROM Permisos")
            permisos = cursor.fetchall()
        
        # Asignar todos los permisos al rol Administrador
        permisos_asignados = 0
        for permiso in permisos:
            permiso_id = permiso[0]
            # Verificar si ya existe la asignación
            cursor.execute("""
                SELECT COUNT(*) FROM RolPermisos 
                WHERE RolID = ? AND PermisoID = ?
            """, rol_id, permiso_id)
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO RolPermisos (RolID, PermisoID)
                    VALUES (?, ?)
                """, rol_id, permiso_id)
                permisos_asignados += 1
        
        conexion.commit()
        print(f"Se asignaron {permisos_asignados} permisos al rol Administrador")
        return True
    except Exception as error:
        print(f"Error al asignar permisos: {error}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)

def crear_permisos_basicos():
    """Crea los permisos básicos del sistema si no existen"""
    conexion = conectar()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        # Verificar si ya existen permisos
        cursor.execute("SELECT COUNT(*) FROM Permisos")
        if cursor.fetchone()[0] > 0:
            print("Los permisos ya existen")
            return True
        
        # Crear permisos básicos
        permisos = [
            ('ver_ventas', 'Ver ventas', 'ventas'),
            ('crear_ventas', 'Crear ventas', 'ventas'),
            ('editar_ventas', 'Editar ventas', 'ventas'),
            ('eliminar_ventas', 'Eliminar ventas', 'ventas'),
            ('ver_compras', 'Ver compras', 'compras'),
            ('crear_compras', 'Crear compras', 'compras'),
            ('editar_compras', 'Editar compras', 'compras'),
            ('eliminar_compras', 'Eliminar compras', 'compras'),
            ('ver_productos', 'Ver productos', 'inventario'),
            ('crear_productos', 'Crear productos', 'inventario'),
            ('editar_productos', 'Editar productos', 'inventario'),
            ('eliminar_productos', 'Eliminar productos', 'inventario'),
            ('ver_usuarios', 'Ver usuarios', 'usuarios'),
            ('crear_usuarios', 'Crear usuarios', 'usuarios'),
            ('editar_usuarios', 'Editar usuarios', 'usuarios'),
            ('eliminar_usuarios', 'Eliminar usuarios', 'usuarios'),
            ('ver_reportes', 'Ver reportes', 'reportes'),
            ('ver_configuracion', 'Ver configuración', 'configuracion'),
            ('editar_configuracion', 'Editar configuración', 'configuracion'),
            ('admin_completo', 'Acceso completo de administrador', 'sistema'),
        ]
        
        for nombre, descripcion, modulo in permisos:
            cursor.execute("""
                INSERT INTO Permisos (Nombre, Descripcion, Modulo)
                VALUES (?, ?, ?)
            """, nombre, descripcion, modulo)
        
        conexion.commit()
        print(f"Se crearon {len(permisos)} permisos básicos")
        return True
    except Exception as error:
        print(f"Error al crear permisos: {error}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)

def crear_usuario_admin(contraseña='admin123'):
    """
    Crea el usuario admin con todos los permisos
    
    Args:
        contraseña: Contraseña para el usuario admin (default: 'admin123')
    
    Returns:
        True si se creó correctamente, False en caso contrario
    """
    conexion = conectar()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        # Verificar si el usuario admin ya existe
        cursor.execute("SELECT UsuarioID FROM Usuarios WHERE NombreUsuario = 'admin'")
        resultado = cursor.fetchone()
        
        if resultado:
            usuario_id = resultado[0]
            print("Usuario 'admin' ya existe")
            
            # Verificar que tenga el rol Administrador
            cursor.execute("""
                SELECT u.RolID FROM Usuarios u
                INNER JOIN Roles r ON u.RolID = r.RolID
                WHERE u.UsuarioID = ? AND r.Nombre = 'Administrador'
            """, usuario_id)
            
            if not cursor.fetchone():
                # Actualizar el rol a Administrador
                rol_admin_id = crear_rol_administrador()
                if rol_admin_id:
                    cursor.execute("""
                        UPDATE Usuarios SET RolID = ? WHERE UsuarioID = ?
                    """, rol_admin_id, usuario_id)
                    conexion.commit()
                    print("Usuario admin actualizado con rol Administrador")
            
            # Asegurar que tenga todos los permisos
            cursor.execute("SELECT RolID FROM Usuarios WHERE UsuarioID = ?", usuario_id)
            rol_id = cursor.fetchone()[0]
            asignar_todos_permisos_administrador(rol_id)
            
            return True
        
        # Crear rol Administrador si no existe
        rol_admin_id = crear_rol_administrador()
        if not rol_admin_id:
            print("Error: No se pudo crear el rol Administrador")
            return False
        
        # Crear permisos básicos si no existen
        crear_permisos_basicos()
        
        # Asignar todos los permisos al rol Administrador
        asignar_todos_permisos_administrador(rol_admin_id)
        
        # Crear el usuario admin
        password_hash = hash_password(contraseña)
        cursor.execute("""
            INSERT INTO Usuarios (NombreUsuario, ClaveHash, RolID, Estado)
            VALUES (?, ?, ?, 1)
        """, 'admin', password_hash, rol_admin_id)
        
        conexion.commit()
        print(f"Usuario 'admin' creado correctamente con contraseña: {contraseña}")
        print("IMPORTANTE: Cambia la contraseña después del primer inicio de sesión")
        return True
        
    except Exception as error:
        print(f"Error al crear usuario admin: {error}")
        conexion.rollback()
        return False
    finally:
        cerrar_conexion(conexion)

# Variable global para almacenar el usuario actual
usuario_actual = None

def establecer_usuario_actual(usuario_data):
    """Establece el usuario actual del sistema"""
    global usuario_actual
    usuario_actual = usuario_data

def obtener_usuario_actual():
    """Obtiene el usuario actual del sistema"""
    return usuario_actual

def obtener_gestor_permisos():
    """Obtiene una instancia del gestor de permisos para el usuario actual"""
    global usuario_actual
    if usuario_actual:
        return GestorPermisos(usuario_actual['UsuarioID'])
    return None

# ======================================
# INICIALIZACIÓN AUTOMÁTICA
# ======================================

def inicializar_sistema_admin():
    """
    Inicializa el sistema creando el usuario admin con todos los permisos
    Ejecuta esta función al iniciar la aplicación por primera vez
    """
    print("=" * 50)
    print("INICIALIZANDO SISTEMA - USUARIO ADMIN")
    print("=" * 50)
    
    # Crear permisos básicos
    crear_permisos_basicos()
    
    # Crear rol Administrador
    rol_admin_id = crear_rol_administrador()
    
    # Asignar todos los permisos al rol Administrador
    if rol_admin_id:
        asignar_todos_permisos_administrador(rol_admin_id)
    
    # Crear usuario admin
    crear_usuario_admin()
    
    print("=" * 50)
    print("INICIALIZACIÓN COMPLETA")
    print("=" * 50)
    print("\nUsuario creado:")
    print("  Usuario: admin")
    print("  Contraseña: admin123")
    print("  Rol: Administrador")
    print("  Permisos: Todos los permisos del sistema")
    print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer inicio de sesión")

# Ejecutar al importar el módulo (opcional)
if __name__ == "__main__":
    inicializar_sistema_admin()

