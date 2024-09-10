from django.contrib import admin
from .models import Player, Room

admin.site.register(Player)


# Define the inline for Player model
class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0  # No extra blank forms to be displayed
    fields = ['user', 'room']  # Fields to display in the inline


# Register the Room model with the PlayerInline
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ['id', 'link', 'status']
