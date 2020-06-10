from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError(u'Unsupported File Extension.')

class Document(models.Model):
    summary_p = models.IntegerField(validators=[MinValueValidator(5), MaxValueValidator(50)])
    document = models.FileField(validators=[validate_file_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Summary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    original_link = models.TextField()
    date_created = models.DateTimeField()

    def __str__(self):
        return self.original_link
