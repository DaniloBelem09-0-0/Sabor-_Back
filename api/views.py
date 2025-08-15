from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

auth_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de autenticação'),
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

@swagger_auto_schema(
    method='post',
    operation_description="Autenticação de usuário",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response('Login bem-sucedido', schema=auth_response_schema),
        400: openapi.Response('Credenciais inválidas', schema=error_response_schema)
    }
)
@api_view(['POST'])
def login_view(request):
    """Endpoint para autenticação de usuários"""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'status': 'success',
            'token': token.key,
            'user_id': user.id
        })
    return Response(
        {'status': 'error', 'message': 'Credenciais inválidas'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@swagger_auto_schema(
    method='post',
    operation_description="Encerra a sessão do usuário",
    responses={
        200: openapi.Response(description="Logout bem-sucedido"),
        401: openapi.Response(description="Não autorizado")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'status': 'success'})

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        operation_description="Registro de novo usuário",
        responses={
            201: openapi.Response(
                description="Usuário criado",
                schema=UserSerializer
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@swagger_auto_schema(
    method='get',
    operation_description="Endpoint de teste da API",
    responses={
        200: openapi.Response(
            description="Sucesso",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'version': openapi.Schema(type=openapi.TYPE_STRING),
                            'author': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        )
    }
)
@api_view(['GET'])
def test_endpoint(request):
    data = {
        'message': 'API está funcionando!',
        'status': 'success',
        'data': {
            'version': '1.0',
            'author': 'Seu Nome'
        }
    }
    return Response(data)