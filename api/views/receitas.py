# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.serializers import RecipeSerializer

from rest_framework import generics, permissions, status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

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
    serializer = RecipeSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(author=request.user)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
