from google import genai
from django.conf import settings
from decouple import config


# this file needs changes


        # AI model
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class GeminiService:

    @staticmethod
    def ask_ai(query, context=""):



        """
        gets query from user and return answer
        
        :param query: user query
        :param context: referance context (similar context)
        Return:
            str : ai responce based on query and context
        """

        full_prompt = f"""
        Answer the question based on the context below:
        Context:
        {context}

        Question:
        {query}
        """

        response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )        
        return response.text
    


