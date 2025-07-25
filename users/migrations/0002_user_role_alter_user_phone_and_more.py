# Generated by Django 5.0 on 2025-07-09 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('manager', 'Manager'), ('client', 'Client')], default='client', help_text='Определяет уровень доступа в системе', max_length=10, verbose_name='Роль пользователя'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, help_text='Формат: +79991234567', max_length=20, null=True, verbose_name='Телефон'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['role'], name='users_user_role_36d76d_idx'),
        ),
    ]
