from django.contrib import admin

from .models import BlackjackPlayer, BlackjackRoom

admin.site.register(BlackjackPlayer)


# Define the inline for Player model
class PlayerInline(admin.TabularInline):
    model = BlackjackPlayer
    extra = 0  # No extra blank forms to be displayed
    fields = ['chips', 'current_hand_value']  # Fields to display in the inline


# Register the Room model with the PlayerInline
@admin.register(BlackjackRoom)
class RoomAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]
    list_display = ['id', 'name', 'status']
