from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Recipe  
from .models import Ingredient

from .models import PreparationStep

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


# serializers.py
class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    steps = serializers.StringRelatedField(many=True, read_only=True)  # 👈 mudou de preparation_steps para steps

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'title', 'difficulty', 'prep_time',
            'ingredients', 'steps', 'state', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.StringRelatedField(many=True, read_only=True)
    steps = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


# Para criar/editar ingrediente
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'measure_unit']
        read_only_fields = ['id']
        

# Para exibir ingrediente com recipe apenas como ID
class IngredientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'measure_unit', 'recipe']


# Para detalhar ingrediente junto com receita (se quiser trazer dados da receita)
class IngredientDetailSerializer(serializers.ModelSerializer):
    recipe = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'measure_unit', 'recipe']


class PreparationStepSerializer(serializers.ModelSerializer):
    # Exibir a receita apenas pelo ID
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = PreparationStep
        fields = ['id', 'order', 'description', 'recipe']
        read_only_fields = ['id']

    def validate_order(self, value):
        if value <= 0:
            raise serializers.ValidationError("A ordem do passo deve ser maior que zero.")
        return value