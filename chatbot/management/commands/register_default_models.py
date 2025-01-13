from django.core.management.base import BaseCommand
from chatbot.models import AIModel

class Command(BaseCommand):
    help = 'Register default AI models'

    def handle(self, *args, **kwargs):
        default_models = [
            {
                'name': 'Claude',
                'display_name': 'Claude',
                'description': 'Anthropic\'s Claude AI assistant',
                'model_type': 'claude',
                'is_active': True,
                'api_key_required': True,
                'system_prompt': "You are Claude, an AI assistant created by Anthropic. You aim to be helpful while being direct and honest."
            },
            {
                'name': 'gpt-4',
                'display_name': 'GPT-4',
                'description': 'OpenAI\'s most capable model',
                'model_type': 'openai',
                'is_active': True,
                'api_key_required': True,
                'system_prompt': "You are a helpful AI assistant."
            },
            {
                'name': 'gpt-3.5-turbo',
                'display_name': 'GPT-3.5',
                'description': 'OpenAI\'s efficient and capable model',
                'model_type': 'openai',
                'is_active': True,
                'api_key_required': True,
                'system_prompt': "You are a helpful AI assistant."
            }
        ]

        for model_data in default_models:
            AIModel.objects.get_or_create(
                name=model_data['name'],
                defaults=model_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully registered default models')) 