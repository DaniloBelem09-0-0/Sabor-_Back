from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views import RegisterView, login_view, test_endpoint

schema_view = get_schema_view(
    openapi.Info(
        title="Sabor API",
        default_version='v1',
        description="Documentação da API Sabor",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@sabor.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/login/', login_view, name='login'),  # Corrigido: removido .as_view()
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/test/', test_endpoint, name='test-endpoint'),
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
]