from django.shortcuts import render

# start the game on loading the page
def homepage(request):
    return render(request, 'homepage.html')

