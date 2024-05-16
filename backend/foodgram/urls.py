from django.contrib import admin
from django.urls import path, include
from api.views import redirect_to_full_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/<str:short_link>/', redirect_to_full_link),
]