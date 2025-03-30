from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('flashie', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lectureslide',
            name='title',
            field=models.CharField(blank=True, max_length=200, default=''),
            preserve_default=True,
        ),
    ] 