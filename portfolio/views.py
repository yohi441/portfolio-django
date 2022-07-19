from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View
from django.core.mail import send_mail
from .forms import ContactForm
import time



class LazyLoadingImg(View):
    template_name=""

    def get(self, request):

        if request.htmx:
            return render(request, self.template_name)

        return redirect(reverse('index'))



def index(request):
    form = ContactForm()
    template_name = 'index.html'
    return render(request, template_name, {'form': form})


def send_contact_email(request):
    if request.htmx:
        if request.method == "POST":
            
            form = ContactForm(request.POST)
            if form.is_valid():    
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                message = form.cleaned_data['message']
                
                try:
                    send_mail(
                        f"Message from {name}. Email: {email}",
                        f"{message}",
                        f"{email}",
                        ['rikou92991@gmail.com'],
                        fail_silently=False,
                    )
                except:     
                    return render(request, 'partials/send_email_exception.html', {'form': form })

                form = ContactForm()
                return render(request, 'partials/contact_valid_form.html', {'form': form})

            return render(request, 'partials/contact_invalid_form.html', {'form': form})
    return redirect(reverse('index'))
   


