from django.db import migrations

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    if not User.objects.filter(username='django').exists():
        User.objects.create_superuser('django', 'admin@example.com', 'ChangeThisPassword')

class Migration(migrations.Migration):

    dependencies = [
        ('quotationbot', '0006_alter_chatserversettings_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
