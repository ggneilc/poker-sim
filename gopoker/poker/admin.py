from django.contrib import admin
from .models import PokerPlayer, PokerRoom, PokerMessages

# Register your models here.
admin.site.register(PokerPlayer)
admin.site.register(PokerRoom)
admin.site.register(PokerMessages)
