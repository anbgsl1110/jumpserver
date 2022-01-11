# Generated by Django 3.1.13 on 2022-01-04 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perms', '0020_auto_20210910_1103'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='applicationpermission',
            options={'ordering': ('name',), 'permissions': [('view_myapps', 'Can view my apps'), ('connect_myapps', 'Can connect my apps'), ('view_userapps', 'Can view user apps'), ('view_usergroupapps', 'Can view usergroup apps')], 'verbose_name': 'Application permission'},
        ),
        migrations.AlterModelOptions(
            name='assetpermission',
            options={'ordering': ('name',), 'permissions': [('view_myassets', 'Can view my assets'), ('connect_myassets', 'Can connect my assets'), ('view_userassets', 'Can view user assets'), ('view_usergroupassets', 'Can view usergroup assets')], 'verbose_name': 'Asset permission'},
        ),
    ]