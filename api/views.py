from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Credenciais inválidas'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

@login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'status': 'success'})

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Credenciais inválidas'}, status=400)

## End point de testes
def test_endpoint(request):
    data = {
        'message': 'API está funcionando!',
        'status': 'success',
        'data': {
            'version': '1.0',
            'author': 'Seu Nome'
        }
    }
    return JsonResponse(data)