from django.db import models
from django.contrib.auth.models import Group, User
import random
import string
from django.utils import timezone
from datetime import timedelta
from ua.models import UnidadAdministrativa


class Whitelist(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="perfil"
    )
    rol = models.ForeignKey(Group, on_delete=models.CASCADE)
    ua = models.ForeignKey(
        UnidadAdministrativa, on_delete=models.SET_NULL, null=True, blank=True
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.email} - {self.rol.name}"


class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        return "".join(random.choices(string.digits, k=6))

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
