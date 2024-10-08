from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm
from .models import Player
import random
import string


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = form.save(commit=False)
            # Set the chosen password
            new_user.set_password(form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Log in the user and redirect to home page
            login(request, new_user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,
                            username=username, password=password)
        if user is not None:
            login(request, user)
            response = JsonResponse({'status': 'success'})
            response['HX-Redirect'] = r'/'
            return response
    else:
        return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return render(request, 'homepage.html')


def home(request):
    user = request.user
    if user.is_authenticated:
        player, created = Player.objects.get_or_create(user=user)
        if created:
            player.save()
    return render(request, 'homepage.html')


def genRandomID():
    # Define the character set: uppercase letters and digits
    characters = string.ascii_uppercase + string.digits

    # Generate a random 6-character ID
    room_id = ''.join(random.choice(characters) for _ in range(6))

    return room_id
