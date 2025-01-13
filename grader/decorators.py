from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Teacher
from django.core.exceptions import PermissionDenied

def teacher_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if request.user.is_authenticated and Teacher.objects.filter(user=request.user).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Access denied. Teachers only.')
                raise PermissionDenied 
        except:
            messages.error(request, 'Access denied. Teachers only.')
            raise PermissionDenied 
    return _wrapped_view 