# Generated by Django 2.0.7 on 2019-12-22 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20191220_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='place',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='Order', to='user.Place'),
        ),
    ]