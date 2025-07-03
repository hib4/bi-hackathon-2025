from tortoise import fields, models
import uuid

class Quiz(models.Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    question = fields.TextField()
    answer_A = fields.TextField()
    answer_B = fields.TextField()
    answer_C = fields.TextField()
    correct_answer = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    book = fields.ForeignKeyField(
        "models.Book",
        related_name="quizzes",
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "quizzes"

    def __str__(self):
        return self.question
