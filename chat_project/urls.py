from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from chat.views import logout_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
]

# ✅ Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ Serve static files in development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
