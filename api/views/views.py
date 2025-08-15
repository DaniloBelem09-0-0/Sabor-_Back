from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from api.serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserSerializerEdit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


User = get_user_model()

# Schema Swagger para edição de usuário
edit_user_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Novo username", default=None),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Novo email", default=None),
    }
)


# Schemas Swagger
auth_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'token': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'message': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# ------------------ LOGIN ------------------
@swagger_auto_schema(
    method='post',
    operation_description="Autenticação de usuário",
    request_body=UserLoginSerializer,
    responses={
        200: openapi.Response('Login bem-sucedido', schema=auth_response_schema),
        400: openapi.Response('Credenciais inválidas', schema=error_response_schema),
        401: openapi.Response('Não autorizado', schema=error_response_schema)
    }
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'status': 'success',
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    })


# ------------------ LOGOUT ------------------
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


# ------------------ REGISTRO ------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Registro de novo usuário",
        request_body=UserRegisterSerializer,
        responses={
            201: openapi.Response(
                description="Usuário criado com sucesso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description="Dados inválidos", schema=error_response_schema)
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # já cria com senha hash

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'username': user.username,
            'email': user.email,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


##-------------------------------------------------------------------------------------------
@api_view(['GET'])
def test_endpoint(request):
    return Response({
        'message': 'API está funcionando!',
        'status': 'success',
        'data': {
            'version': '1.0',
            'author': 'Seu Nome'
        }
    })


@api_view(['GET'])
def get_login(request):
    if request.user.is_authenticated:
        return Response({
            'status': 'Usuário já logado',
            'user_info': {
                'id': request.user.id,
                'username': request.user.username,
                'email': getattr(request.user, 'email', ''),
            }
        })
    return Response({'error': 'Usuário não logado'}, status=status.HTTP_400_BAD_REQUEST)


#-----------------------------------------------------------------------------------------------
@swagger_auto_schema(
    method='patch',
    operation_description="Edita username e email do usuário logado (campos opcionais)",
    request_body=UserSerializerEdit,
    responses={
        200: openapi.Response('Usuário atualizado com sucesso', schema=UserSerializerEdit),
        400: openapi.Response('Dados inválidos', schema=error_response_schema)
    }
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def edit_user(request):
    user = request.user
    serializer = UserSerializerEdit(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#---------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, id):
    try:
        target_user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if target_user == request.user:
        return Response({'error': 'Você não pode seguir a si mesmo'}, status=status.HTTP_400_BAD_REQUEST)

    request.user.following.add(target_user)
    return Response({'status': f'Você está seguindo {target_user.username}'}, status=status.HTTP_200_OK)

#---------------------------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, id):
    try:
        target_user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    request.user.following.remove(target_user)
    return Response({'status': f'Você deixou de seguir {target_user.username}'}, status=status.HTTP_200_OK)