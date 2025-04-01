# Generated by Django 5.1.5 on 2025-02-01 07:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatss', '0002_accuser_last_online_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupchat',
            name='members',
            field=models.ManyToManyField(related_name='group_menbers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='from_who',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chatss.groupchat'),
        ),
        migrations.AlterField(
            model_name='message',
            name='to_who',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
