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
def search_recipe_byId(request, id):
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


@swagger_auto_schema(
    method='get',
    operation_description="Busca receitas com filtros opcionais",
    manual_parameters=[
        openapi.Parameter('title', openapi.IN_QUERY, description="Filtrar por título", type=openapi.TYPE_STRING),
        openapi.Parameter('difficulty', openapi.IN_QUERY, description="Filtrar por dificuldade", type=openapi.TYPE_STRING),
        openapi.Parameter('prep_time', openapi.IN_QUERY, description="Filtrar por tempo de preparo máximo (em minutos)", type=openapi.TYPE_INTEGER),
        openapi.Parameter('state', openapi.IN_QUERY, description="Estado da receita", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response('Receitas encontradas com sucesso', schema=RecipeSerializer(many=True)),
        404: 'Nenhuma receita encontrada'
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_recipe(request):
    queryset = Recipe.objects.all() 

    title = request.query_params.get('title')
    difficulty = request.query_params.get('difficulty')
    prep_time = request.query_params.get('prep_time')
    state = request.query_params.get('state')  # corrigido

    if title:
        queryset = queryset.filter(title__icontains=title)
    if difficulty:
        queryset = queryset.filter(difficulty=difficulty)
    if prep_time:
        queryset = queryset.filter(prep_time__lte=prep_time)
    if state:
        queryset = queryset.filter(state__iexact=state)  # corrigido

    if not queryset.exists():
        return Response({'error': 'Nenhuma receita encontrada'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RecipeSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@swagger_auto_schema(
    method='get',
    operation_description="Busca uma receita de forma aleatória",
    responses={
        200: openapi.Response('Receita encontrada com sucesso', schema=RecipeSerializer()),
        404: 'Nenhuma receita encontrada'
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def random_recipe(request):
    queryset = Recipe.objects.all() 

    if not queryset.exists():
        return Response({'error': 'Nenhuma receita encontrada'}, status=status.HTTP_404_NOT_FOUND)

    # Seleciona 1 receita aleatória
    recipe = queryset.order_by("?").first()

    serializer = RecipeSerializer(recipe)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    operation_description="Deleta uma receita do usuário logado pelo id",
    responses={
        204: openapi.Response('Receita deletada com sucesso', schema=RecipeSerializer()),
        404: 'Nenhuma receita encontrada'
    }
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_recipe(request, id):
    try:
        target_recipe = Recipe.objects.get(id=id)
        if(target_recipe.author != request.user):
            return Response(
                    {"detail": "Você não tem permissão para deletar esta receita."},
                    status=status.HTTP_403_FORBIDDEN
                )
        target_recipe.delete()
        return Response(
            {"detail": "Receita deletada com sucesso."},
            status=status.HTTP_204_NO_CONTENT
            )
    except Recipe.DoesNotExist:
        return Response(
            {"detail": "Receita não encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )


@swagger_auto_schema(
    method='patch',
    operation_description="Atualiza parcialmente uma receita (somente o autor pode editar).",
    request_body=RecipeSerializer,
    
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID da receita",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter('title', openapi.IN_QUERY, description="Filtrar por título", type=openapi.TYPE_STRING),
        openapi.Parameter('difficulty', openapi.IN_QUERY, description="Filtrar por dificuldade", type=openapi.TYPE_STRING),
        openapi.Parameter('prep_time', openapi.IN_QUERY, description="Filtrar por tempo de preparo máximo (em minutos)", type=openapi.TYPE_INTEGER),
        openapi.Parameter('state', openapi.IN_QUERY, description="Estado da receita", type=openapi.TYPE_STRING),
    ],
    responses={
        200: RecipeSerializer,
        403: "Sem permissão",
        404: "Receita não encontrada",
        400: "Dados inválidos"
    }
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def patch_recipe(request, id):
    try:
        target_recipe = Recipe.objects.get(pk=id)

        if target_recipe.author != request.user:
            return Response(
                {"detail": "Você não tem acesso a essa receita"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RecipeSerializer(target_recipe, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Recipe.DoesNotExist:
        return Response(
            {"detail": "Receita não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
