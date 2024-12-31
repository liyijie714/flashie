from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Product, Vote
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages

# Create your views here.
def home(request):
    products = Product.objects.order_by('-votes_total')[:5]  # Get top 5 by votes
    return render(request, 'products/home.html', {'products': products})

@login_required(login_url='/accounts/login')
def create(request):
    if request.method == 'POST':
        if request.POST['title'] and request.POST['body'] and request.POST['url'] and request.FILES['icon'] and request.FILES['image']:
            product = Product()
            product.title = request.POST['title']
            product.body = request.POST['body']
            product.url = request.POST['url']
            product.icon = request.FILES['icon']
            product.image = request.FILES['image']
            product.hunter = request.user
            product.pub_date = timezone.datetime.now()
            product.save()
            return redirect('products:detail', product.id)
    else:
        return render(request, 'products/create.html', {'error': 'All fields are required.'})

def detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/detail.html', {'product': product})

def edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    return render(request, 'products/edit.html', {'product': product})

def delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('home')

@login_required(login_url='/accounts/login')
def upvote(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        try:
            vote = Vote(user=request.user, product=product)
            vote.save()
            product.votes_total += 1
            product.save()
        except IntegrityError:
            messages.error(request, "You've already voted for this product!")
        return redirect('products:detail', product_id)
