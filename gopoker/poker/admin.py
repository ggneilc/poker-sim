from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(PokerPlayer)
admin.site.register(PokerRoom)
admin.site.register(PokerMessages)