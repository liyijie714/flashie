from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import AIModel, Role, ChatHistory
from .openai_integration import OpenAIChat
from .claude_integration import ClaudeChat
import json

@login_required
def chat_home(request):
    models = AIModel.objects.filter(is_active=True)
    roles = Role.objects.filter(user=request.user)
    return render(request, 'chatbot/chat_home.html', {
        'models': models,
        'roles': roles
    })

def get_chat_instance(model_type, api_key=None):
    if model_type == 'openai':
        return OpenAIChat(api_key)
    elif model_type == 'claude':
        return ClaudeChat(api_key)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        model_name = data.get('model', '')
        api_key = data.get('api_key', '')
        role_id = data.get('role_id')

        model = get_object_or_404(AIModel, name=model_name)
        chat_instance = get_chat_instance(model.model_type, api_key)

        system_prompt = model.system_prompt
        if role_id:
            role = get_object_or_404(Role, id=role_id, user=request.user)
            system_prompt = role.role_description

        response = chat_instance.generate_response(system_prompt, message)

        # Save chat history
        ChatHistory.objects.create(
            user=request.user,
            role_id=role_id,
            model=model,
            message=message,
            response=response
        )

        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        model_name = data.get('model', '')
        api_key = data.get('api_key', '')
        role_id = data.get('role_id')

        model = get_object_or_404(AIModel, name=model_name)
        chat_instance = get_chat_instance(model.model_type, api_key)

        system_prompt = model.system_prompt
        if role_id:
            role = get_object_or_404(Role, id=role_id, user=request.user)
            system_prompt = role.role_description

        response = chat_instance.generate_response(system_prompt, message)

        # Save chat history
        ChatHistory.objects.create(
            user=request.user,
            role_id=role_id,
            model=model,
            message=message,
            response=response
        )

        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def save_role(request):
    try:
        data = json.loads(request.body)
        role_name = data.get('name')
        role_description = data.get('description', '')
        greeting = data.get('greeting', '')

        # Create or update the role
        role, created = Role.objects.update_or_create(
            user=request.user,
            role_name=role_name,
            defaults={
                'role_description': role_description,
                'greeting': greeting
            }
        )

        return JsonResponse({
            'status': 'success',
            'role': {
                'id': role.id,
                'name': role.role_name,
                'description': role.role_description,
                'greeting': role.greeting
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_roles(request):
    """Get all roles for the current user"""
    try:
        roles = Role.objects.filter(user=request.user)
        roles_data = [{
            'id': role.id,
            'name': role.role_name,
            'description': role.role_description,
            'greeting': role.greeting
        } for role in roles]
        
        return JsonResponse({
            'status': 'success',
            'roles': roles_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_chat_history(request):
    """Get chat history for the current user"""
    try:
        role_id = request.GET.get('role_id')
        
        # Base query filtering by user
        query = ChatHistory.objects.filter(user=request.user)
        
        # Add role filter if role_id is provided
        if role_id:
            query = query.filter(role_id=role_id)
        
        # Order by creation date
        chat_history = query.order_by('created_at')
        
        history_data = [{
            'id': chat.id,
            'message': chat.message,
            'response': chat.response,
            'created_at': chat.created_at.isoformat(),
            'role_id': chat.role_id,
            'model': chat.model.name if chat.model else None
        } for chat in chat_history]
        
        return JsonResponse({
            'status': 'success',
            'history': history_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def debug_models(request):
    """Debug view to check available models and their configurations"""
    try:
        models = AIModel.objects.all()
        models_data = [{
            'id': model.id,
            'name': model.name,
            'display_name': model.display_name,
            'description': model.description,
            'model_type': model.model_type,
            'is_active': model.is_active,
            'api_key_required': model.api_key_required,
            'system_prompt': model.system_prompt
        } for model in models]
        
        return JsonResponse({
            'status': 'success',
            'models': models_data,
            'total_count': len(models_data)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_role(request):
    """Create a new character role"""
    try:
        data = json.loads(request.body) if request.body else request.POST
        
        # Create new role
        role = Role.objects.create(
            user=request.user,
            role_name=data.get('name', ''),
            role_description=data.get('description', ''),
            greeting=data.get('greeting', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'role': {
                'id': role.id,
                'role_name': role.role_name,
                'role_description': role.role_description,
                'greeting': role.greeting
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# Add any other views you need...