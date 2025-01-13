from .models import Teacher

def teacher_status(request):
    is_teacher = False
    if request.user.is_authenticated:
        is_teacher = Teacher.objects.filter(user=request.user).exists()
    return {'is_teacher': is_teacher} 