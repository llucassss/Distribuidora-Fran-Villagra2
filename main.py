from kivy.app import App
from kivy.core.window import Window 
from kivy.lang import Builder
import os
import sys

# Agregar directorio de pantalla al path
ruta_pantallas = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mkdir_pantallas')
if ruta_pantallas not in sys.path:
    sys.path.insert(0, ruta_pantallas)

from login import LoginScreen

class DistribuidoraApp(App):
    def build(self):
        # Color de fondo de la ventana
        Window.clearcolor = (0.95, 0.95, 0.97, 1)

        # Cargar el archivo .kv del login con ruta absoluta
        kv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mkdir_pantallas', 'login_sc.kv')
        if os.path.exists(kv_path):
            Builder.load_file(kv_path)
            print(f"Archivo .kv cargado: {kv_path}")
        else:
            print(f"Error: No se encontró el archivo .kv en: {kv_path}")

        # Pantalla login
        return LoginScreen()

if __name__ == "__main__":
    DistribuidoraApp().run()