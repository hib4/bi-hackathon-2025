from tortoise import fields, models
import uuid

class Page(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    content = fields.TextField()
    image_url = fields.TextField()
    audio_url = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    book = fields.ForeignKeyField(
        "models.Book",
        related_name="pages",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "pages"

    def __str__(self):
        return self.content
