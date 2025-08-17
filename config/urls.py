from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views.views import RegisterView, login_view, test_endpoint, get_login, logout_view, edit_user, follow_user, unfollow_user
from api.views.receitas import create_recipe, search_recipe

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
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication Endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/signup/', RegisterView.as_view(), name='register'),
    path('auth/me/', get_login, name='get_me'),
    path('auth/logout/', logout_view, name='logout'),

    # Usuário
    path('users/', edit_user, name='edit_user_logado'),
    path('users/<id>/follow', follow_user, name='seguir usuários'),
    path('users/<id>/unfollow', unfollow_user, name='deixar de seguir'),

    # Receitas
    path('recipes/', create_recipe, name='criar receitas'),
    path('recipes/<id>', search_recipe, name='Busca uma receitas'),


    # Test Endpoint
    path('test/', test_endpoint, name='test-endpoint'),
    
    # Documentation
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