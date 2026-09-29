from django.db import migrations


def create_identifier_table(apps, schema_editor):
    patient_model = apps.get_model('Core', 'Patient')
    identifier_field = patient_model._meta.get_field('identified_by_users')
    through_model = identifier_field.remote_field.through
    table_name = through_model._meta.db_table

    if table_name not in schema_editor.connection.introspection.table_names():
        schema_editor.create_model(through_model)


def remove_identifier_table(apps, schema_editor):
    patient_model = apps.get_model('Core', 'Patient')
    identifier_field = patient_model._meta.get_field('identified_by_users')
    through_model = identifier_field.remote_field.through
    table_name = through_model._meta.db_table

    if table_name in schema_editor.connection.introspection.table_names():
        schema_editor.delete_model(through_model)


class Migration(migrations.Migration):
    dependencies = [
        ('Core', '0050_patient_identified_by_users'),
    ]

    operations = [
        migrations.RunPython(
            create_identifier_table,
            remove_identifier_table,
        ),
    ]
