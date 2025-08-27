from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class State(models.TextChoices):
    AC = 'AC', _('Acre')
    AL = 'AL', _('Alagoas')
    AP = 'AP', _('Amapá')
    AM = 'AM', _('Amazonas')
    BA = 'BA', _('Bahia')
    CE = 'CE', _('Ceará')
    DF = 'DF', _('Distrito Federal')
    ES = 'ES', _('Espírito Santo')
    GO = 'GO', _('Goiás')
    MA = 'MA', _('Maranhão')
    MT = 'MT', _('Mato Grosso')
    MS = 'MS', _('Mato Grosso do Sul')
    MG = 'MG', _('Minas Gerais')
    PA = 'PA', _('Pará')
    PB = 'PB', _('Paraíba')
    PR = 'PR', _('Paraná')
    PE = 'PE', _('Pernambuco')
    PI = 'PI', _('Piauí')
    RJ = 'RJ', _('Rio de Janeiro')
    RN = 'RN', _('Rio Grande do Norte')
    RS = 'RS', _('Rio Grande do Sul')
    RO = 'RO', _('Rondônia')
    RR = 'RR', _('Roraima')
    SC = 'SC', _('Santa Catarina')
    SP = 'SP', _('São Paulo')
    SE = 'SE', _('Sergipe')
    TO = 'TO', _('Tocantins')


class User(AbstractUser):

    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )
    
    email = models.EmailField(_('email address'), unique=True)
    profile = models.CharField(
        max_length=10,
        choices=[
            ('COMUM', 'Comum'),
            ('AUTOR', 'Autor'),
            ('ADMIN', 'Administrador'),
        ],
        default='COMUM'
    )
    state = models.CharField(
        _('UF'),
        max_length=2,
        choices=State.choices,
        blank=True
    )
    avatar_url = models.URLField(_('URL do Avatar'), blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups')
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Recipe(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'FACIL', _('Fácil')
        MEDIUM = 'MEDIO', _('Médio')
        HARD = 'DIFICIL', _('Difícil')

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(_('título'), max_length=255)
    difficulty = models.CharField(_('dificuldade'), max_length=7, choices=Difficulty.choices)
    prep_time = models.PositiveIntegerField(_('tempo de preparo'), help_text=_("Tempo em minutos"))
    state = models.CharField(_('UF'), max_length=2, choices=State.choices, blank=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('receita')
        verbose_name_plural = _('receitas')
        ordering = ['-created_at']

    def __str__(self):
        return self.title




class Ingredient(models.Model):
    """
    Model for recipe ingredients.
    """
    name = models.CharField(
        _('nome'),
        max_length=255
    )
    quantity = models.DecimalField(
        _('quantidade'),
        max_digits=6,
        decimal_places=2
    )
    measure_unit = models.CharField(
        _('unidade de medida'),
        max_length=50,
        blank=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name=_('receita')
    )

    class Meta:
        verbose_name = _('ingrediente')
        verbose_name_plural = _('ingredientes')

    def __str__(self):
        return f"{self.quantity} {self.measure_unit} de {self.name}"


class PreparationStep(models.Model):
    """
    Model for recipe preparation steps.
    """
    order = models.PositiveIntegerField(_('ordem'))
    description = models.TextField(_('descrição'))
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name=_('receita')
    )

    class Meta:
        verbose_name = _('passo de preparo')
        verbose_name_plural = _('passos de preparo')
        ordering = ['order']

    def __str__(self):
        return f"Passo {self.order} - {self.description[:50]}..."


class Comment(models.Model):
    """
    Model for recipe comments.
    """
    text = models.TextField(_('texto'))
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('usuário')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('receita')
    )
    created_at = models.DateTimeField(
        _('criado em'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('comentário')
        verbose_name_plural = _('comentários')
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentário de {self.user} em {self.recipe}"


class Rating(models.Model):
    """
    Model for recipe ratings.
    """
    rating = models.PositiveIntegerField(
        _('avaliação'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('usuário')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('receita')
    )

    class Meta:
        verbose_name = _('avaliação')
        verbose_name_plural = _('avaliações')
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"Avaliação {self.rating} estrelas de {self.user} para {self.recipe}"


class Favorite(models.Model):
    """
    Model for user favorite recipes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('usuário')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('receita')
    )

    class Meta:
        verbose_name = _('favorito')
        verbose_name_plural = _('favoritos')
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.recipe} favoritada por {self.user}"


class Media(models.Model):
    """
    Model for recipe media (images/videos).
    """

    class MediaType(models.TextChoices):
        IMAGE = 'IMAGEM', _('Imagem')
        VIDEO = 'VIDEO', _('Vídeo')

    url = models.URLField(_('URL'))
    type = models.CharField(
        _('tipo'),
        max_length=6,
        choices=MediaType.choices
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name=_('receita')
    )

    class Meta:
        verbose_name = _('mídia')
        verbose_name_plural = _('mídias')

    def __str__(self):
        return f"{self.get_type_display()} para {self.recipe}"


class Report(models.Model):
    """
    Model for content reports.
    """

    class Reason(models.TextChoices):
        SPAM = 'SPAM', _('Spam')
        INAPPROPRIATE = 'CONTEUDO_IMPROPRIO', _('Conteúdo Impróprio')
        DISRESPECTFUL = 'DESRESPEITOSO', _('Desrespeitoso')
        OTHER = 'OUTRO', _('Outro')

    class Status(models.TextChoices):
        PENDING = 'PENDENTE', _('Pendente')
        UNDER_REVIEW = 'ANALISE', _('Em Análise')
        RESOLVED = 'RESOLVIDO', _('Resolvido')
        REJECTED = 'REJEITADO', _('Rejeitado')

    class ContentType(models.TextChoices):
        RECIPE = 'RECEITA', _('Receita')
        COMMENT = 'COMENTARIO', _('Comentário')

    reason = models.CharField(
        _('motivo'),
        max_length=20,
        choices=Reason.choices
    )
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_('usuário')
    )
    content_id = models.PositiveIntegerField(_('ID do conteúdo'))
    content_type = models.CharField(
        _('tipo de conteúdo'),
        max_length=10,
        choices=ContentType.choices
    )
    created_at = models.DateTimeField(
        _('criado em'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('denúncia')
        verbose_name_plural = _('denúncias')

    def __str__(self):
        return f"Denúncia de {self.user} sobre {self.get_content_type_display()}"


class Notification(models.Model):
    """
    Model for user notifications.
    """

    class NotificationType(models.TextChoices):
        FOLLOWER = 'SEGUIDOR', _('Novo seguidor')
        COMMENT = 'COMENTARIO', _('Novo comentário')
        RATING = 'AVALIACAO', _('Nova avaliação')
        FAVORITE = 'FAVORITO', _('Receita favoritada')

    type = models.CharField(
        _('tipo'),
        max_length=10,
        choices=NotificationType.choices
    )
    read = models.BooleanField(
        _('lida'),
        default=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('usuário')
    )
    data = models.JSONField(
        _('dados'),
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('criado em'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('notificação')
        verbose_name_plural = _('notificações')
        ordering = ['-created_at']

    def __str__(self):
        return f"Notificação {self.get_type_display()} para {self.user}"