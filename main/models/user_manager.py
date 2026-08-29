from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from main.models.base import TimeStampedModel


class UserManager(TimeStampedModel):
    """
    Manager user entity (Web portal manager).
    Responsible for creating and managing restaurants.
    """
    first_name = models.CharField(max_length=100, verbose_name="Primeiro Nome")
    last_name = models.CharField(max_length=100, verbose_name="Sobrenome")
    phone_number = models.CharField(max_length=20, verbose_name="Número de Telefone")
    path_photo = models.CharField(max_length=255, null=True, blank=True, verbose_name="Caminho da Foto")
    password = models.CharField(max_length=255, verbose_name="Senha Hash")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Último Login")
    email = models.EmailField(unique=True, max_length=255, db_index=True, verbose_name="E-mail")
    username = models.CharField(unique=True, max_length=100, db_index=True, verbose_name="Nome de Usuário")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_admin = models.BooleanField(default=False, verbose_name="Administrador")

    class Meta:
        db_table = 'user_manager'
        verbose_name = 'Gerente'
        verbose_name_plural = 'Gerentes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def user_type(self):
        return "ADMIN" if self.is_admin else "MANAGER"

    @property
    def restaurant_count(self):
        """
        Dynamically calculates the number of restaurants owned by this manager.
        Avoids redundant and inconsistent database column persistence.
        """
        return self.restaurants.count()

    def set_password(self, raw_password):
        """
        Securely hashes and sets the user's password using Django's PBKDF2 algorithm.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Validates the raw password against the stored secure cryptographic hash.
        """
        return check_password(raw_password, self.password)
