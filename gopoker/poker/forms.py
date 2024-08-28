from django.forms import ModelForm
from django import forms 
from .models import *

class ChatmessageCreateForm(ModelForm):
  class Meta:
    model = PokerMessages
    fields = ['body']
    widgets = {
      'body' : forms.TextInput(attrs={'placeholder': 'Your Message (press enter to send)', 'class': 'chatbar', 'maxlength' : '300', 'autofocus': True})
    }