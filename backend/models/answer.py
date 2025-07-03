from tortoise import fields, models
import uuid

class Answer(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    selected_answer = fields.TextField()
    is_correct = fields.BooleanField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    quiz = fields.ForeignKeyField(
        "models.Quiz",
        related_name="answers",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "answers"

    def __str__(self):
        return self.selected_answer
