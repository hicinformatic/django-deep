from django.db import models


gender_choices = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'),)


class BaseModel(models.Model):
    """
    Base model class for all models in the application.
    This class provides a common structure and functionality for all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    time_at = models.TimeField(auto_now=True)
    date_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Role(BaseModel):
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
