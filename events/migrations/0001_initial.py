# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import bitfield.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('slug', models.SlugField(unique=True, max_length=200, verbose_name='slug')),
            ],
            options={
                'verbose_name': 'calendar',
                'verbose_name_plural': 'calendar',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CalendarRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField()),
                ('distinction', models.CharField(max_length=20, null=True, verbose_name='distinction', blank=True)),
                ('limit_choices_to', models.TextField(default='{}', help_text='This field is for filtering the available choices. The content should be a JSON-formatted object. The keys are the field name with optional lookup suffix. The values are the required value for that field.', null=True, verbose_name='limit choices', blank=True)),
                ('inheritable', models.BooleanField(default=True, verbose_name='inheritable')),
                ('calendar', models.ForeignKey(related_name='calendarrelation', verbose_name='calendar', to='events.Calendar')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'calendar relation',
                'verbose_name_plural': 'calendar relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appropriate_for', bitfield.models.BitField([b'Educator', b'Informal Educator', b'Family', b'Student', b'Kid'], default=31, verbose_name='appropriate for')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('end', models.DateTimeField(help_text='The end time must be later than the start time.', verbose_name='end')),
                ('all_day', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('end_recurring_period', models.DateTimeField(help_text='This date is ignored for one time only events.', null=True, verbose_name='Ends on', blank=True)),
                ('calendar', models.ForeignKey(related_name='events', to='events.Calendar')),
                ('creator', models.ForeignKey(related_name='creator', verbose_name='creator', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'get_latest_by': 'start',
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField()),
                ('distinction', models.CharField(max_length=20, null=True, verbose_name='distinction', blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('event', models.ForeignKey(verbose_name='event', to='events.Event')),
            ],
            options={
                'verbose_name': 'event relation',
                'verbose_name_plural': 'event relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, null=True, verbose_name='title', blank=True)),
                ('description', models.TextField(null=True, verbose_name='description', blank=True)),
                ('start', models.DateTimeField(verbose_name='start')),
                ('end', models.DateTimeField(verbose_name='end')),
                ('all_day', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False, verbose_name='cancelled')),
                ('original_start', models.DateTimeField(verbose_name='original start')),
                ('original_end', models.DateTimeField(verbose_name='original end')),
                ('event', models.ForeignKey(verbose_name='event', to='events.Event')),
            ],
            options={
                'ordering': ('start',),
                'verbose_name': 'occurrence',
                'verbose_name_plural': 'occurrences',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('frequency', models.CharField(max_length=10, verbose_name='frequency', choices=[('YEARLY', 'Yearly'), ('MONTHLY', 'Monthly'), ('WEEKLY', 'Weekly'), ('DAILY', 'Daily'), ('HOURLY', 'Hourly'), ('MINUTELY', 'Minutely'), ('SECONDLY', 'Secondly')])),
                ('params', models.TextField(null=True, verbose_name='params', blank=True)),
            ],
            options={
                'verbose_name': 'rule',
                'verbose_name_plural': 'rules',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='rule',
            field=models.ForeignKey(related_name='events', blank=True, to='events.Rule', help_text="Select '----' for a one time only event.", null=True, verbose_name='Repeats'),
            preserve_default=True,
        ),
    ]
