from tortoise import fields, models
from enum import Enum
import uuid

class AuthType(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"

class User(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.TextField()
    google_id = fields.TextField(null=True)
    auth = fields.CharEnumField(AuthType, max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.name
