from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Tech Studio API",
        default_version="v1",
        description="Tech Studio Commiunty API. Buliding a community for everyone",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="oludarenathaniel@gmail.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)