import openai
from typing import List, Dict

class OpenAIChat:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> str:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_response(self, system_prompt: str, user_message: str, model: str = "gpt-3.5-turbo") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.chat(messages, model) 