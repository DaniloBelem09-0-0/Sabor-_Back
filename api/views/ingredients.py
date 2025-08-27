from api.serializers import IngredientSerializer, PreparationStepSerializer
from api.models import Ingredient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from api.models import Recipe
from django.shortcuts import get_object_or_404

ingredient_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'quantity', 'unit'],  # campos obrigatórios do seu serializer
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nome do ingrediente'),
        'quantity': openapi.Schema(type=openapi.TYPE_NUMBER, description='Quantidade do ingrediente'),
        'unit': openapi.Schema(type=openapi.TYPE_STRING, description='Unidade de medida'),
    },
)

@swagger_auto_schema(
    method='post',
    operation_description="Cria um novo ingrediente vinculado a uma receita do usuário logado",
    request_body=ingredient_schema,
    manual_parameters=[
        openapi.Parameter(
            'id_recipe',
            openapi.IN_PATH,
            description="ID da receita à qual o ingrediente será adicionado",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        201: openapi.Response('Ingrediente criado com sucesso', ingredient_schema),
        400: 'Dados inválidos',
        403: 'Usuário não é o autor da receita',
        404: 'Receita não encontrada'
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_ingredient(request, id_recipe):
    recipe = get_object_or_404(Recipe, id=id_recipe, author=request.user)
    serializer = IngredientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(recipe=recipe) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_description="Deleta um ingrediente do usuário logado pelo id",
    responses={
        204: openapi.Response('Ingrediente deletado com sucesso', schema=IngredientSerializer()),
        404: 'Nenhum ingrediente encontrado'
    }
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_ingredient(request, id):
    try:
        target_ingredient = Ingredient.objects.get(id=id)
        if(target_ingredient.recipe.author != request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        target_ingredient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Ingredient.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)