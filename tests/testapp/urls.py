from django.urls import include, path

urlpatterns = [
    path("ht/", include("health_check.urls")),
]
