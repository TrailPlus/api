import os
import subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# ----------------- CONFIGURACIÓN ----------------- #

CLAVE_ENCRIPTACION = b'0123456789abcdef'  # Debe ser de 16, 24 o 32 bytes (AES-128, AES-192, AES-256)
CARPETA_ORIGEN = "json_pruebas"  # Asegúrate de que esta carpeta contiene los archivos JSON a encriptar
CARPETA_DESTINO = "p-coding"    # Carpeta en el repositorio donde se guardarán los archivos encriptados
MENSAJE_COMMIT = "Exit-P"

# ----------------- RUTA BASE DEL PROYECTO ----------------- #

# Detecta la ubicación real del script (asumimos que está dentro del repo)
RUTA_REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(RUTA_REPO)  # Nos aseguramos de estar en el repo

# Ruta completa para carpetas
RUTA_ORIGEN = os.path.join(RUTA_REPO, CARPETA_ORIGEN)
RUTA_DESTINO = os.path.join(RUTA_REPO, CARPETA_DESTINO)

# Crea carpeta destino si no existe
os.makedirs(RUTA_DESTINO, exist_ok=True)

def encriptar_archivo(nombre_archivo, clave):
    cipher = AES.new(clave, AES.MODE_CBC)  # Usamos el modo CBC de AES
    ruta_origen = os.path.join(RUTA_ORIGEN, nombre_archivo)
    ruta_destino = os.path.join(RUTA_DESTINO, nombre_archivo + ".json")

    # Leer solo el contenido del archivo (en este caso JSON)
    with open(ruta_origen, "r", encoding="utf-8") as archivo:
        datos = archivo.read()

    # Encriptar el contenido de texto del archivo con padding
    datos_encriptados = cipher.encrypt(pad(datos.encode('utf-8'), AES.block_size))

    # Guardar el archivo encriptado con IV al principio (solo el contenido)
    with open(ruta_destino, "wb") as archivo_out:
        archivo_out.write(cipher.iv)  # Guardamos el IV (vector de inicialización)
        archivo_out.write(datos_encriptados)

    print(f"✅ Encriptado: {nombre_archivo}")

def encriptar_todos():
    for archivo in os.listdir(RUTA_ORIGEN):
        if archivo.endswith(".json"):
            try:
                encriptar_archivo(archivo, CLAVE_ENCRIPTACION)
            except Exception as e:
                print(f"❌ Error con {archivo}: {e}")

def git_add_commit_push():
    try:
        # Agregar todos los archivos encriptados a git
        subprocess.run(["git", "add", "."], check=True)  # Agregar todos los archivos cambiados en el repo

        # Verifica si hay algo que realmente se va a commitear
        resultado = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not resultado.stdout.strip():
            print("🟡 No hay cambios nuevos para commitear.")
            return

        # Si hay cambios, hace commit y push
        subprocess.run(["git", "commit", "-m", MENSAJE_COMMIT], check=True)
        subprocess.run(["git", "push"], check=True)

        print("🚀 Archivos encriptados subidos exitosamente a GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar comandos Git: {e}")


def borrar_archivo(nombre_archivo):
    ruta_archivo = os.path.join(RUTA_ORIGEN, nombre_archivo)
    
    # Listar archivos en la carpeta de origen para verificar
    print("Archivos en la carpeta:", os.listdir(RUTA_ORIGEN))
    
    if os.path.exists(ruta_archivo):
        # Eliminar archivo de la carpeta local
        os.remove(ruta_archivo)
        print(f"✅ Archivo {nombre_archivo} borrado localmente.")

        # Eliminar el archivo de Git
        subprocess.run(["git", "rm", ruta_archivo], check=True)
        subprocess.run(["git", "commit", "-m", f"Eliminar archivo {nombre_archivo}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"✅ Archivo {nombre_archivo} eliminado de GitHub.")
    else:
        print(f"❌ El archivo {nombre_archivo} no existe en la carpeta local.")


def menu():
    print("Seleccione una opción:")
    print("1. Agregar (Encriptar archivos)")
    print("2. Borrar archivo")
    print("3. Salir")

    opcion = input("Ingrese el número de la opción: ")

    if opcion == "1":
        encriptar_todos()
        git_add_commit_push()
    elif opcion == "2":
        archivo_a_borrar = input("Ingrese el nombre del archivo a borrar: ")
        borrar_archivo(archivo_a_borrar)
    elif opcion == "3":
        print("Saliendo...")
        exit()
    else:
        print("❌ Opción no válida.")
        menu()

# --- MAIN --- #
if __name__ == "__main__":
    menu()
