# Generated by Django 3.1.13 on 2022-01-10 07:37

from django.db import migrations, models

from common.utils.timezone import as_current_tz
from orgs.utils import tmp_to_root_org


def fill_ticket_serial_number(apps, schema_editor):
    with tmp_to_root_org():
        Ticket = apps.get_model('tickets', 'Ticket')
        tickets = Ticket.objects.all().order_by('date_created')

        curr_day = '00000000'
        curr_num = 1

        print(f'\nFill ticket serial number ... ', end='')
        for ticket in tickets:
            # 跑这个脚本的时候，所有 ticket.serial_num == null
            date_created = as_current_tz(ticket.date_created)
            date_str = date_created.strftime('%Y%m%d')
            if date_str != curr_day:
                curr_day = date_str
                curr_num = 1

            ticket.serial_num = curr_day + '%04d' % curr_num
            curr_num += 1

        Ticket.objects.bulk_update(tickets, fields=('serial_num',))
        print(len(tickets), end='')


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_ticketsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='serial_num',
            field=models.CharField(max_length=128, null=True, unique=True, verbose_name='Serial number'),
        ),
        migrations.RunPython(fill_ticket_serial_number),
    ]
