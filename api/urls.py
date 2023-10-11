from django.views.generic import RedirectView
from swagger.swagger import schema_view
from django.contrib import admin
from django.urls import path,include,re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/jobs/', include("jobs.urls")),
    path("auth/",include("users.urls",namespace= "auth")),
    path("api/users/",include("users.urls2",namespace= "user")),
    path("api/notifications/",include("notifications.urls",namespace="notification")),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', RedirectView.as_view(url='swagger/', permanent=False), name='index'),
]
