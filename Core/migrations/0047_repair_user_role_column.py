from django.db import migrations


def add_role_column(apps, schema_editor):
    user_model = apps.get_model('Core', 'User')
    column_names = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            user_model._meta.db_table,
        )
    }
    if 'role' not in column_names:
        schema_editor.add_field(user_model, user_model._meta.get_field('role'))


def remove_role_column(apps, schema_editor):
    user_model = apps.get_model('Core', 'User')
    column_names = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            user_model._meta.db_table,
        )
    }
    if 'role' in column_names:
        schema_editor.remove_field(user_model, user_model._meta.get_field('role'))


class Migration(migrations.Migration):
    dependencies = [
        ('Core', '0046_user_role'),
    ]

    operations = [
        migrations.RunPython(add_role_column, remove_role_column),
    ]
