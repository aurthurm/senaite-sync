from django.core.management.base import BaseCommand
import csv, datetime
import dateutil.parser
import pandas as pd
from apps.patients.models import Patient
from apps.facility.models import Facility

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Uploading Patients ... Please wait! ....'))
        path = kwargs['path']
        with open(path, 'rt') as f:
            patients = pd.read_csv(f)
            # patients = patients[:2]
            i = 1
            for row in patients.iterrows():
                pruid=row[1]["PrimaryReferrerUID"]
                try:
                    facility = Facility.objects.get(fuid__exact=pruid)
                except Facility.DoesNotExist:
                    facility = None

                if facility != None:
                    Patient.objects.get_or_create(
                        name=row[1]["Firstname"],
                        surname=row[1]["Surname"],
                        gender=row[1]["Gender"],
                        dob=dateutil.parser.parse(row[1]["BirthDate"], ignoretz=True),
                        cpid=row[1]["ClientPatientID"],
                        puid=row[1]["UID"],
                        pruid=row[1]["PrimaryReferrerUID"],
                        anonymous=False,
                        facility=facility
                    )                
                    self.stdout.write(self.style.SUCCESS(f'Added {i} Patient'))
                    i+=1
                else:                
                    self.stdout.write(self.style.ERROR(f'Facility {pruid} not found. Patient {row[1]["UID"]} skipped'))


        self.stdout.write(self.style.SUCCESS('DONE'))

# python manage.py load_questions --path /path/to/your/file.csv