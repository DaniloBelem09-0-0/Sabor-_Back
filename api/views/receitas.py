# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializers import RecipeSerializer

from rest_framework import generics, permissions, status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import Recipe

@swagger_auto_schema(
    method='post',
    operation_description="Cria uma nova receita para o usuário logado",
    request_body=RecipeSerializer,
    responses={
        201: openapi.Response('Receita criada com sucesso', schema=RecipeSerializer),
        400: 'Dados inválidos'
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_recipe(request):
    print("Usuário atual:", request.user)
    print("is_authenticated:", request.user.is_authenticated)

    serializer = RecipeSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(author=request.user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Busca uma receita pelo ID para o usuário logado",
    responses={
        200: openapi.Response('Receita encontrada com sucesso', schema=RecipeSerializer),
        404: 'Receita não encontrada'
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_recipe(request, id):
    print("caiuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
    try:
        # Busca a receita pelo ID
        print("id", id)
        target_recipe = Recipe.objects.get(pk=id)
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Receita não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Serializa o objeto antes de retornar
    serializer = RecipeSerializer(target_recipe)
    return Response(serializer.data, status=status.HTTP_200_OK)