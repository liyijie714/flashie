from typing import List, Dict
import anthropic

class ClaudeChat:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], model: str = "claude-3-opus-20240229") -> str:
        try:
            # Convert messages to Claude format
            prompt = ""
            for message in messages:
                if message["role"] == "system":
                    prompt += f"{message['content']}\n\n"
                elif message["role"] == "user":
                    prompt += f"Human: {message['content']}\n\n"
                elif message["role"] == "assistant":
                    prompt += f"Assistant: {message['content']}\n\n"
            
            response = self.client.messages.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_response(self, system_prompt: str, user_message: str, model: str = "claude-3-opus-20240229") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.chat(messages, model) 