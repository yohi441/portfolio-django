from django.urls import path
from . import views_htmx
from . import views


htmx_url_patterns = [
    # send_email
    path('email/send', views.send_contact_email, name='contact_email'),
    # frontend
    path('javascript/lazy', views_htmx.javascript, name="javascript_lazy"),
    path('css/lazy', views_htmx.css, name="css_lazy"),
    path('alpine/lazy', views_htmx.alpine, name="alpine_lazy"),
    path('html/lazy', views_htmx.html, name="html_lazy"),
    path('htmx/lazy', views_htmx.htmx, name="htmx_lazy"),
    path('tailwind/lazy', views_htmx.tailwind, name="tailwind_lazy"),
    path('vue/lazy', views_htmx.vue, name="vue_lazy"),
    # backend
    path('python/lazy', views_htmx.python, name="python_lazy"),
    path('django/lazy', views_htmx.django, name="django_lazy"),
    path('postgresql/lazy', views_htmx.postgresql, name="postgresql_lazy"),
    path('redis/lazy', views_htmx.redis, name="redis_lazy"),
    # tools
    path('git/lazy', views_htmx.git, name="git_lazy"),
    path('linux/lazy', views_htmx.linux, name="linux_lazy"),
    # portfolio
    path('portfolio/1/lazy', views_htmx.portfolio_1, name="portfolio_1"),
    path('portfolio/2/lazy', views_htmx.portfolio_2, name="portfolio_2"),
    path('portfolio/3/lazy', views_htmx.portfolio_3, name="portfolio_3"),
]