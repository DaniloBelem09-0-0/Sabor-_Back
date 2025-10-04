from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views.views import RegisterView, login_view, test_endpoint, get_login, logout_view, edit_user, follow_user, unfollow_user
from api.views.receitas import create_recipe, search_recipe, search_recipe_byId, favorite_recipe_byId, random_recipe, delete_recipe, patch_recipe, create_steps, get_ingredients_by_recipe_id, delete_step
from api.views.ingredients import create_ingredient, delete_ingredient
from api.views.comments import get_list_comments_byId, create_comment_byId, delete_comment_byId, rating_recipe_byId, get_rating_recipe_byId

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

    path('auth/login/', login_view, name='login'),
    path('auth/signup/', RegisterView.as_view(), name='register'),
    path('auth/me/', get_login, name='get_me'),
    path('auth/logout/', logout_view, name='logout'),

    path('users/', edit_user, name='edit_user_logado'),
    path('users/<id>/follow', follow_user, name='seguir usuários'),
    path('users/<id>/unfollow', unfollow_user, name='deixar de seguir'),

    path('recipes/', search_recipe, name='buscar_receitas'),               # GET → lista/filtra
    path('recipes/<int:id>/', search_recipe_byId, name='buscar_receita_id'),  # GET → por id
    path('recipes/create/', create_recipe, name='criar_receita'),             # POST → criar
    path('recipes/random/', random_recipe, name='receita_aleatoria'),        # GET → aleatória
    path('recipes/<id>', delete_recipe, name='Usuário criador da receita pode deletar uma das suas receitas'),
    path('recipes/edite/<id>', patch_recipe, name='Usuário pode editar uma de suas receitas'),
    path('recipes/<id>/steps/', create_steps, name="create-steps"),
    path('recipes/<id_recipe>/steps/<id_step>', delete_step, name='delete-step'),

    path('ingredients/<id_recipe>', create_ingredient, name='create-ingredient'),      # POST → criar ingrediente
    path('ingredients/<int:id>/', delete_ingredient, name='delete-ingredient'), 
    path('ingredients/recipe/<id>', get_ingredients_by_recipe_id, name='get-recipe-by-id'),
    
    path('comments/recipe/<int:id>', get_list_comments_byId, name='get the list of a recipe' ),
    path('comments/recipe/<int:id>/create', create_comment_byId, name='create a comment at one recipe'),
    path('test/', test_endpoint, name='test-endpoint'),
    path('comments/<int:id>', delete_comment_byId, name='delete comment by id'),

    path('rattings/recipes/<int:id>', rating_recipe_byId, name='Ratting recipe by id'),
    path('rattings/recipes/<int:id>/avaliation', get_rating_recipe_byId, name='Ratting recipe by id'),

    path('favorite/recipes/<int:id>', favorite_recipe_byId, name='Favorite recipe by id'),

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