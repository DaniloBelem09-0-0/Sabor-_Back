from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Recipe  # Import your custom User model


# Serializer para registro de usuário
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=True)  # obrigatório

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile', 'state', 'avatar_url')
        extra_kwargs = {
            'profile': {'required': False, 'default': 'COMUM'},
            'state': {'required': False},
            'avatar_url': {'required': False}
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile=validated_data.get('profile', 'COMUM'),
            state=validated_data.get('state', ''),
            avatar_url=validated_data.get('avatar_url', '')
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Forneça email e password.")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Credenciais inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Usuário desativado.")

        data['user'] = user
        return data


# Serializer para exibir dados do usuário (sem senha)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'profile', 'state', 'avatar_url', 'following', 'followers')
        read_only_fields = ('id', 'following', 'followers')


class UserSerializerEdit(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ['email', 'profile', 'state', 'avatar_url']
        extra_kwargs = {
            'profile': {'required': False},
            'state': {'required': False},
            'avatar_url': {'required': False}
        }

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso.")
        return value


# Serializers de receitas
class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Changed from 'author' to 'user'
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    preparation_steps = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'title', 'difficulty', 'prep_time',
                  'ingredients', 'preparation_steps', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class RecipeDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']