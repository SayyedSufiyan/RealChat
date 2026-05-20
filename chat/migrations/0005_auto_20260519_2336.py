from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_superuser(apps, schema_editor):
    User = apps.get_model("auth", "User")

    username = "admin"
    email = "admin@gmail.com"
    password = "admin123456"

    user, created = User.objects.get_or_create(username=username)

    user.email = email
    user.password = make_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0004_friendrequest"),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]