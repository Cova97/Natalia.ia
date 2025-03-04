from services.voice_service import VoiceService
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API de OpenAI desde las variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    # Verificar si la clave de API está configurada
    if not OPENAI_API_KEY:
        raise ValueError("La clave de API de OpenAI no está configurada. Asegúrate de tener un archivo .env con OPENAI_API_KEY.")

    # Crear una instancia del servicio de voz
    natalia = VoiceService(OPENAI_API_KEY)

    # Iniciar el asistente de voz
    natalia.run()