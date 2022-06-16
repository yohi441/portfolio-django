from .views import LazyLoadingImg



javascript = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/javascript_lazy.html")
alpine = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/alpine_lazy.html")
html = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/html_lazy.html")
htmx = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/htmx_lazy.html")
tailwind = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/tailwind_lazy.html")
vue = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/vue_lazy.html")
css = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/frontend/css_lazy.html")


python = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/backend/python_lazy.html")
django = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/backend/django_lazy.html")
postgresql = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/backend/postgresql_lazy.html")
redis = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/backend/redis_lazy.html")

git = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/tools/git_lazy.html")
linux = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/tools/linux_lazy.html")


portfolio_1 = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/portfolio_1.html")
portfolio_2 = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/portfolio_2.html")
portfolio_3 = LazyLoadingImg.as_view(template_name="htmx_partials_lazy_images/portfolio_3.html")