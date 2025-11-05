import os
from openai import AsyncOpenAI
from django.conf import settings

class ChatAIHandler:
    def __init__(self):
        # Initialize the async OpenAI client
        api_key = os.getenv('OPENAI_API_KEY', settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None)
        self.client = AsyncOpenAI(api_key=api_key) if api_key else None
        
    async def get_ai_response(self, message, context=None):
        try:
            if not self.client:
                return "Lo siento, el servicio de AI no está configurado correctamente. Un agente te atenderá pronto."

            # Create system message for context
            system_message = """Eres un asistente amable y profesional de Speedy Transfer, 
            un servicio de transferencias de dinero. Proporciona respuestas breves, 
            precisas y útiles en español. Sé cortés y profesional en todo momento."""

            # Prepare conversation history
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": message}
            ]

            if context:
                messages.extend(context)

            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                presence_penalty=0
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error in AI response generation: {str(e)}")
            return "Lo siento, hay un problema técnico. Un agente te atenderá pronto."