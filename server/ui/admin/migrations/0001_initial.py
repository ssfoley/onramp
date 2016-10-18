# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-18 01:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='job',
            fields=[
                ('job_id', models.AutoField(primary_key=True, serialize=False)),
                ('job_name', models.TextField()),
                ('state', models.IntegerField(default=0)),
                ('output_file', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='module',
            fields=[
                ('module_id', models.AutoField(primary_key=True, serialize=False)),
                ('module_name', models.CharField(max_length=255, unique=True)),
                ('version', models.TextField(default=b'')),
                ('src_location', models.TextField(default=b'')),
                ('description', models.TextField(default=b'')),
            ],
        ),
        migrations.CreateModel(
            name='module_to_pce',
            fields=[
                ('pm_pair_id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.IntegerField(default=0)),
                ('src_location_type', models.TextField(default=b'local')),
                ('src_location_path', models.TextField(default=b'')),
                ('install_location', models.TextField(default=b'')),
                ('is_visible', models.BooleanField(default=True)),
                ('module_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.module')),
            ],
        ),
        migrations.CreateModel(
            name='pce',
            fields=[
                ('pce_id', models.AutoField(primary_key=True, serialize=False)),
                ('pce_name', models.CharField(max_length=255, unique=True)),
                ('ip_addr', models.TextField(default=b'127.0.0.1')),
                ('ip_port', models.IntegerField(default=0)),
                ('state', models.IntegerField(default=0)),
                ('contact_info', models.TextField(default=b'')),
                ('location', models.TextField(default=b'')),
                ('description', models.TextField(default=b'')),
                ('pce_username', models.TextField(default=b'onramp')),
            ],
        ),
        migrations.CreateModel(
            name='user_to_workspace',
            fields=[
                ('uw_pair_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='workspace',
            fields=[
                ('workspace_id', models.AutoField(primary_key=True, serialize=False)),
                ('workspace_name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='workspace_to_pce_module',
            fields=[
                ('wpm_pair_id', models.AutoField(primary_key=True, serialize=False)),
                ('pm_pair_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.module_to_pce')),
                ('workspace_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.workspace')),
            ],
        ),
        migrations.AddField(
            model_name='user_to_workspace',
            name='workspace_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.workspace'),
        ),
        migrations.AddField(
            model_name='module_to_pce',
            name='pce_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.pce'),
        ),
        migrations.AddField(
            model_name='job',
            name='module_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.module'),
        ),
        migrations.AddField(
            model_name='job',
            name='pce_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.pce'),
        ),
        migrations.AddField(
            model_name='job',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='job',
            name='workspace_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin.workspace'),
        ),
        migrations.AlterUniqueTogether(
            name='workspace_to_pce_module',
            unique_together=set([('workspace_id', 'pm_pair_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='user_to_workspace',
            unique_together=set([('user_id', 'workspace_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='module_to_pce',
            unique_together=set([('pce_id', 'module_id')]),
        ),
    ]
