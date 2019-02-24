from django.core.management.base import BaseCommand
import csv
import pandas as pd
from apps.facility.models import Facility

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Uploading Facilities ... Please wait! ....'))
        path = kwargs['path']
        with open(path, 'rt') as f:
            clients = pd.read_csv(f)
            # clients = clients[:2]
            for row in clients.iterrows():
                Facility.objects.get_or_create(
                    name=row[1]["Name"],
                    state=row[1]["State"],
                    district=row[1]["District"],
                    fid=row[1]["ClientID"],
                    fuid=row[1]["Client UID"],
                )

        self.stdout.write(self.style.SUCCESS('DONE'))

# python manage.py load_questions --path /path/to/your/file.csv