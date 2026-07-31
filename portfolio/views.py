from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View
from django.core.mail import send_mail
from .forms import ContactForm



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
            context = {
                'form': form,
                "message": None,
                "message_tags": None
            }
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
                    context['message'] = "An error occurred while sending the email. Please try again later."
                    context['message_tags'] = "text-red-600"
                    return render(request, 'partials/contact_form.html', context)
                
                form = ContactForm()
                context['form'] = form
                context['message'] = "Your message has been sent successfully!"
                context['message_tags'] = "text-green-600"
                return render(request, 'partials/contact_form.html', context)

            return render(request, 'partials/contact_form.html', context)
    return redirect(reverse('index'))
   


