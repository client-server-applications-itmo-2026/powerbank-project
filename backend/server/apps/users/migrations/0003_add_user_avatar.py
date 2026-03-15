# Generated manually for User Profile avatar support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_usermodel_managers"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermodel",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="avatars/%Y/%m/",
                verbose_name="avatar",
            ),
        ),
    ]
