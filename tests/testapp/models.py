from django.db import models
from django.utils import timezone


gender_choices = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'),)


class BaseModel(models.Model):
    """
    Base model class for all models in the application.
    This class provides a common structure and functionality for all models.
    """
    created_at = models.DateTimeField()
    time_at = models.TimeField()
    date_at = models.DateField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        if not self.time_at:
            self.time_at = timezone.now().time()
        if not self.date_at:
            self.date_at = timezone.now().date()
        super().save(*args, **kwargs)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    nb_users = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class User(BaseModel):
    username = models.CharField(max_length=150, unique=True)
    roles = models.ManyToManyField(Role, related_name='roles_to_users')
    gender = models.CharField(max_length=1, blank=True, null=True, choices=gender_choices)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Email(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_to_emails')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
