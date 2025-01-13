from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .decorators import teacher_required
from django.conf import settings
from openai import OpenAI

import os
import base64

client = OpenAI(api_key=settings.OPENAI_API_KEY)


@login_required(login_url='/accounts/login')
@teacher_required
def home(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            # Check if file is an image or text
            is_image = is_image_file(uploaded_file.name)

            if is_image:
                grade_result = grade_image_submission(file_path)
            else:
                with open(file_path, 'r') as file:
                    content = file.read()
                grade_result = grade_text_submission(content)

            # Clean up - delete the uploaded file
            fs.delete(filename)

            context = {
                'grade_result': grade_result
            }
            return render(request, 'grader/home.html', context)

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')

    return render(request, 'grader/home.html')

def is_image_file(filename):
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def grade_image_submission(image_path):

    try:
        # Encode the image
        base64_image = encode_image_to_base64(image_path)

        # Call the API with the image
        response = client.chat.completions.create(model="gpt-4o-mini",  # Make sure to use a vision-capable model
        messages=[
            {
                "role": "system",
                "content": "You are a programming instructor tasked with grading student submissions."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please grade this code submission. Evaluate based on:\n1. Code correctness\n2. Code style and best practices\n3. Efficiency\nProvide a detailed analysis and a score out of 100."
                    },
                    {
                        "type": "image_url",
                        "image_url":{
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000)

        return response.choices[0].message.content

    except Exception as e:
        return f"Error during grading: {str(e)}"

def grade_text_submission(content):

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a math teacher tasked with grading student submissions."
            },
            {
                "role": "user",
                "content": """Please grade the following assignment submission. 
                    Evaluate based on the correctness of the solution.
                    
                    Assignment submission:
                    {content}
                    
                    Provide a detailed analysis and a score out of 100."""
            }
        ])

        return response.choices[0].message.content

    except Exception as e:
        return f"Error during grading: {str(e)}"