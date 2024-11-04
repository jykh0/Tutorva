# Generated by Django 4.1.6 on 2024-11-03 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_schedulesession_notification_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulesession',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='Session Completed'),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_present', models.BooleanField(default=False, verbose_name='Present')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='Remarks')),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                ('marked_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.tutor')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='myapp.schedulesession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='myapp.student')),
            ],
            options={
                'unique_together': {('session', 'student')},
            },
        ),
    ]
