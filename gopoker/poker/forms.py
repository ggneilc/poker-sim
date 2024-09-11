from django.forms import ModelForm
from django import forms 
from .models import *

class ChatmessageCreateForm(ModelForm):
  type = forms.CharField(initial='chat_message', widget=forms.HiddenInput())

  class Meta:
    model = PokerMessages
    fields = ['body', 'type']
    widgets = {
      'body' : forms.TextInput( attrs = {
                'placeholder': 'Your Message (press enter to send)', 
                'class': 'chatbar', 
                'maxlength' : '300', 
                'autofocus': True
      })
    }