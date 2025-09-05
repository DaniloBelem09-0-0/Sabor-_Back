from api.models import Comment, Recipe, Rating
from api.serializers import IngredientSerializer, PreparationStepSerializer,CommentSerializer, RatingSerializer
from api.models import Ingredient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from api.models import Recipe
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from django.db.models import Avg


comment_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['text'],
    properties={
        'text': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Texto do comentário'
        ),
    },
)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_list_comments_byId(request, id):
    try:
        recipe = Recipe.objects.get(pk=id)
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Receita não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    comments = recipe.comments.all()  
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Cria um novo comentário vinculado a uma receita",
    request_body=comment_schema,
    responses={
        201: openapi.Response('Comentário criado com sucesso', CommentSerializer),
        400: 'Dados inválidos',
        404: 'Receita não encontrada'
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_comment_byId(request, id):
    try: 
        target_recipe = Recipe.objects.get(pk=id)
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Receita não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, recipe=target_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_comment_byId(request, id):
    try: 
        target_comment = Comment.objects.get(pk=id)
        if target_comment.user != request.user:
            return Response(
                {"detail": "Você não tem permissão para deletar este comentário."},
                status=status.HTTP_403_FORBIDDEN
            )
        target_comment.delete()
        return Response(
            {"detail": "Comentário deletado com sucesso."},
            status=status.HTTP_204_NO_CONTENT
            )
    except Comment.DoesNotExist:
        return Response(
            {"detail": "Comentário não encontrada."},
            status=status.HTTP_404_NOT_FOUND
        )


rating_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['rating'],
    properties={
        'rating': openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description='Nota da receita (1 a 5)',
            minimum=1,
            maximum=5
        ),
    },
)

@swagger_auto_schema(
    method='post',
    operation_description="Avalia uma receita (1–5). Se o usuário já avaliou, a avaliação será atualizada.",
    request_body=rating_schema,
    manual_parameters=[
        openapi.Parameter(
            'id',
            openapi.IN_PATH,
            description="ID da receita que será avaliada",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Avaliação atualizada com sucesso', RatingSerializer),
        201: openapi.Response('Avaliação criada com sucesso', RatingSerializer),
        400: 'Dados inválidos',
        404: 'Receita não encontrada'
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rating_recipe_byId(request, id):
    recipe = get_object_or_404(Recipe, pk=id)

    rating_value = request.data.get('rating')
    if rating_value is None:
        return Response({'error': 'O campo "rating" é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        rating_value = int(rating_value)
    except ValueError:
        return Response({'error': 'O campo "rating" deve ser um número inteiro'}, status=status.HTTP_400_BAD_REQUEST)

    if rating_value < 1 or rating_value > 5:
        return Response({'error': 'A avaliação deve estar entre 1 e 5'}, status=status.HTTP_400_BAD_REQUEST)


    rating_obj, created = Rating.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={'rating': rating_value}
    )

    serializer = RatingSerializer(rating_obj)

    if created:
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_rating_recipe_byId(request, id):
    try: 
        target_recipe = Recipe.objects.get(pk=id)
    except Recipe.DoesNotExist:
        return Response(
            {'error': 'Receita não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    ratings = target_recipe.ratings.all()
    serializer = RatingSerializer(ratings, many=True)

    total_ratings = ratings.count()
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    return Response({
        'ratings': serializer.data,
        'total_ratings': total_ratings,
        'average_rating': round(average_rating, 2)
    }, status=status.HTTP_200_OK)
