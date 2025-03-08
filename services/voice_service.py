import speech_recognition as sr
import pyttsx3
import openai
import os
from datetime import datetime

class VoiceService:
    def __init__(self, openai_api_key):
        """Inicializa el servicio de voz con configuración mejorada."""
        openai.api_key = openai_api_key
        
        # Configuración de voz mejorada
        self.engine = pyttsx3.init()
        self.listen_timeout = int(os.getenv("LISTEN_TIMEOUT", 5))
        self._configure_voice()
        
        # Reconocedor mejorado
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Comandos locales
        self.deactivation_phrases = {
            "muchas gracias", "adiós", "hasta luego", "gracias", 
            "nos vemos", "chao", "terminar", "desactivar"
        }
        self.local_commands = {
            "hora": self._get_time,
            "fecha": self._get_date,
            "cómo estás": lambda: "¡Estoy funcionando perfectamente!",
        }

    def _configure_voice(self):
        """Configura una voz en español si está disponible."""
        voices = self.engine.getProperty('voices')
        spanish_voices = [v for v in voices if "spanish" in v.name.lower()]
        
        if spanish_voices:
            self.engine.setProperty('voice', spanish_voices[0].id)
        else:
            print("Advertencia: No se encontró voz en español. Usando voz predeterminada.")
        
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 0.9)

    def _get_time(self):
        """Devuelve la hora actual formateada."""
        return datetime.now().strftime("Son las %H:%M")

    def _get_date(self):
        """Devuelve la fecha actual formateada."""
        return datetime.now().strftime("Hoy es %d de %B del %Y")

    def speak(self, text):
        """Función mejorada con manejo de errores."""
        try:
            print(f"Natalia: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error en síntesis de voz: {e}")

    def listen_for_activation(self):
        """Escucha mejorada con ajuste de ruido ambiental."""
        with sr.Microphone() as source:
            print("\n🔴 Modo inactivo. Di 'Natalia' para activar...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=self.listen_timeout)
                    command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                    print(f"Usuario: {command}")
                    
                    if "natalia" in command:
                        self.speak("¿En qué puedo ayudarte?")
                        return True
                        
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error de reconocimiento: {e}")
                    continue

    def listen_for_command(self):
        """Escucha activa con feedback visual."""
        with sr.Microphone() as source:
            print("\n🟢 Escuchando...")
            self.recognizer.adjust_for_ambient_noise(source)
            
            try:
                audio = self.recognizer.listen(source, timeout=self.listen_timeout)
                command = self.recognizer.recognize_google(audio, language="es-ES").lower()
                print(f"Usuario: {command}")
                return command
                
            except sr.WaitTimeoutError:
                self.speak("No escuché tu solicitud. ¿Podrías repetirla?")
                return None
            except Exception as e:
                print(f"Error de audio: {e}")
                return None

    def _handle_local_command(self, command):
        """Maneja comandos locales sin usar OpenAI."""
        for key, action in self.local_commands.items():
            if key in command:
                response = action()
                self.speak(response)
                return True
        return False

    def ask_openai(self, prompt):
        """Consulta mejorada a OpenAI con manejo de contexto."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres Natalia, un asistente virtual en español. Sé concisa y amable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            print(f"Error OpenAI: {e}")
            return "Parece que tengo problemas de conexión. ¿Podrías intentarlo de nuevo?"

    def process_command(self, command):
        """Procesamiento mejorado de comandos."""
        if not command:
            return True
            
        if self.is_deactivation_command(command):
            self.speak("¡Hasta luego! Estaré aquí si me necesitas.")
            return False
            
        if self._handle_local_command(command):
            return True
            
        self.speak("Procesando tu solicitud...")
        response = self.ask_openai(command)
        self.speak(response)
        return True

    def is_deactivation_command(self, command):
        """Detección mejorada de comandos de desactivación."""
        return any(phrase in command for phrase in self.deactivation_phrases)

    def run(self):
        """Bucle principal mejorado."""
        while True:
            try:
                if self.listen_for_activation():
                    active = True
                    while active:
                        command = self.listen_for_command()
                        active = self.process_command(command) if command else True
            except KeyboardInterrupt:
                self.speak("Saliendo del sistema...")
                break
            except Exception as e:
                print(f"Error crítico: {e}")
                self.speak("Voy a reiniciar mi sistema...")