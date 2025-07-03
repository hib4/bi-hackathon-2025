from tortoise import fields, models
import uuid

class Book(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    title = fields.TextField()
    description = fields.TextField()
    cover_image_url = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    user = fields.ForeignKeyField(
        "models.User",
        related_name="books",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "books"

    def __str__(self):
        return self.title
