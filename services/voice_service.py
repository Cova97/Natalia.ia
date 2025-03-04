import speech_recognition as sr
import pyttsx3
import openai

class VoiceService:
    def __init__(self, openai_api_key):
        """Inicializa el servicio de voz y configura OpenAI."""
        # Configuración de OpenAI
        openai.api_key = openai_api_key

        # Inicializar el motor de síntesis de voz
        self.engine = pyttsx3.init()

        # Configuración de la voz
        voices = self.engine.getProperty('voices')  # Obtener las voces disponibles
        self.engine.setProperty('voice', voices[0].id)  # Cambia a voices[1].id para una voz femenina (según el sistema)
        self.engine.setProperty('rate', 180)  # Velocidad de habla (por defecto es 200)
        self.engine.setProperty('volume', 1.0)  # Volumen (0.0 a 1.0)

        # Inicializar el reconocedor de voz
        self.recognizer = sr.Recognizer()

        # Conjunto de comandos de desactivación (más eficiente que una lista)
        self.deactivation_phrases = {
            "muchas gracias por la información",
            "adiós",
            "hasta luego",
            "gracias",
            "nos vemos",
            "chao",
            "terminar",
            "desactivar"
        }

    def speak(self, text):
        """Función para que el asistente hable."""
        print(f"Natalia: {text}")  # Imprimir en consola
        self.engine.say(text)      # Decir el texto
        self.engine.runAndWait()   # Esperar a que termine de hablar

    def listen_for_activation(self):
        """Función para escuchar continuamente hasta que se detecte el comando de activación."""
        with sr.Microphone() as source:
            print("Esperando el comando de activación... Di 'Natalia' para comenzar.")
            while True:
                print("Escuchando...")
                try:
                    audio = self.recognizer.listen(source, timeout=5)  # Escuchar con un timeout de 5 segundos
                    command = self.recognizer.recognize_google(audio, language="es-ES")
                    print(f"Comando reconocido: {command}")
                    if "natalia" in command.lower():
                        self.speak("Hola, soy Natalia. ¿En qué puedo ayudarte?")
                        return True  # Activar el sistema
                except sr.WaitTimeoutError:
                    continue  # Continuar escuchando si no se detecta audio
                except sr.UnknownValueError:
                    print("No se entendió el comando.")
                except sr.RequestError:
                    print("Error al conectar con el servicio de reconocimiento de voz.")

    def listen_for_command(self):
        """Función para escuchar y reconocer comandos de voz después de la activación."""
        with sr.Microphone() as source:
            print("Escuchando tu solicitud...")
            try:
                audio = self.recognizer.listen(source, timeout=5)  # Escuchar con un timeout de 5 segundos
                command = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"Comando reconocido: {command}")
                return command.lower()
            except sr.WaitTimeoutError:
                self.speak("No escuché nada. ¿Puedes repetirlo?")
                return None
            except sr.UnknownValueError:
                self.speak("No entendí lo que dijiste.")
                return None
            except sr.RequestError:
                self.speak("Error al conectar con el servicio de reconocimiento de voz.")
                return None

    def ask_openai(self, prompt):
        """Función para enviar una solicitud a OpenAI y obtener una respuesta."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Usar el modelo GPT-3.5-turbo
                messages=[
                    {"role": "system", "content": "Eres un asistente virtual llamado Natalia. Responde de manera amable y útil."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150  # Limitar la longitud de la respuesta
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error al conectar con OpenAI: {e}")
            return "Lo siento, no pude procesar tu solicitud en este momento."

    def is_deactivation_command(self, command):
        """Verifica si el comando es una frase de desactivación."""
        return any(phrase in command for phrase in self.deactivation_phrases)

    def process_command(self, command):
        """Función para procesar los comandos reconocidos."""
        if self.is_deactivation_command(command):
            self.speak("De nada. ¡Estaré aquí si me necesitas!")
            return False  # Desactivar el sistema
        elif "natalia" in command and "estás ahí" in command:
            self.speak("Sí, estoy aquí. ¿En qué puedo ayudarte?")
            return True  # Mantener el sistema activo
        else:
            # Enviar el comando a OpenAI para obtener una respuesta
            response = self.ask_openai(command)
            self.speak(response)
            return True  # Mantener el sistema activo

    def run(self):
        """Inicia el asistente de voz."""
        while True:
            # Esperar a que se detecte el comando de activación
            if self.listen_for_activation():
                # Escuchar y procesar comandos después de la activación
                active = True
                while active:
                    command = self.listen_for_command()
                    if command:
                        active = self.process_command(command)