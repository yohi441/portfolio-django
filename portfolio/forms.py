from django import forms




class ContactForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Your name',
        'class': 'w-full bg-zinc-900/50 border border-zinc-700 rounded p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-600 transition duration-300'
        }))
    email = forms.EmailField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Your email',
        'class': 'w-full bg-zinc-900/50 border border-zinc-700 rounded p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-600 transition duration-300'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': '4', 
        'placeholder':'Your message',
        'cols':'',
        'class': 'w-full bg-zinc-900/50 border border-zinc-700 rounded p-3 text-white placeholder-neutral-500 focus:outline-none focus:border-red-600 transition duration-300'
        }))