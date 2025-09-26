"""
Quiz service for generating and managing reading comprehension questions.
"""


from google import genai
from dotenv import load_dotenv
from os import getenv



class QuizGenerationService:
    def __init__(self, api_key):
        try:
            self.api_key = getenv("GEMINI_API_KEY")
            self.client = genai.Client(self.api_key)
        except Exception as e:
            print(f"An error has ocurred while trying to initialize the quiz generation service: {e}")
            self.client = None


    def generate_quiz(self, text, num_questions=5):
        """
        Genera un quiz a partir de un texto utilizando un modelo de IA.

        Args:
            text (str): El texto base para el quiz.
            num_questions (int): El número de preguntas a generar.

        Returns:
            str: Un diccionario con las preguntas y respuestas del quiz.
        """
        try:
            prompt = f"Genera un quiz de {num_questions} preguntas con respuestas de opción múltiple a partir del siguiente texto:\n\n{text}"

            response = self.client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"Error al generar el quiz: {e}")
            return None

   