from django.urls import include, re_path

urlpatterns = [
    re_path(r"^ht/", include("health_check.urls")),
]
