from logging import PlaceHolder
from django import forms




class ContactForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Your name',
        'class': 'form-text'
        }))
    email = forms.EmailField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Your email',
        'class': 'form-text'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': '4', 
        'placeholder':'Your message',
        'cols':'',
        'class': 'form-text'
        }))