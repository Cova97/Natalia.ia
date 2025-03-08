from services.voice_service import VoiceService
from dotenv import load_dotenv
import os

# Configuración avanzada
load_dotenv()

# Verificación de variables críticas
required_env_vars = ["OPENAI_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing_vars)}")

# Inicialización del servicio
natalia = VoiceService(os.getenv("OPENAI_API_KEY"))

# Mensaje de inicio personalizado
print("\n" + "="*40)
print("Sistema Natalia - Asistente Virtual V2.0")
print("="*40 + "\n")

# Ejecución principal
try:
    natalia.run()
except Exception as e:
    print(f"Error inesperado: {e}")
finally:
    print("\nSistema apagado correctamente.")