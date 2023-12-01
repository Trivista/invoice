# Generated by Django 4.2.7 on 2023-11-30 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_client_town_settings_town'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='title',
        ),
        migrations.AddField(
            model_name='client',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='client',
            name='erf',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_excl_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoice_incl_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='invoice',
            name='reference',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tax_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('CURRENT', 'CURRENT'), ('EMAIL_SENT', 'EMAIL_SENT'), ('OVERDUE', 'OVERDUE'), ('PARTIALLY PAID', 'PARTIALLY PAID'), ('FULLY PAID', 'FULLY PAID'), ('CREDITED', 'CREDITED')], default='CURRENT', max_length=100),
        ),
    ]
