from django.core.management.base import BaseCommand
from django.contrib.staticfiles import finders
import json

from core.models import Region, Province, Municipality, Barangay

class Command(BaseCommand):
    help = 'Load data from ph-address.json into the database and ensure names are in Proper caps'

    def handle(self, *args, **kwargs):
        file_path = finders.find('plugins/ph-address/ph-address.json')

        if not file_path:
            self.stdout.write(self.style.ERROR('Failed to find the ph-address.json in static files'))
            return

        with open(file_path, 'r') as file:
            data = json.load(file)

            for region_code, region_data in data.items():
                region_name_proper = region_data['region_name'].title()
                region, created = Region.objects.get_or_create(code=region_code, name=region_name_proper)
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Added Region: {region.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Found existing Region: {region.name}'))

                for province_name, province_data in region_data['province_list'].items():
                    province_name_proper = province_name.title()
                    province, created = Province.objects.get_or_create(region=region, name=province_name_proper)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'  Added Province: {province.name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  Found existing Province: {province.name}'))

                    for municipality_name, municipality_data in province_data['municipality_list'].items():
                        municipality_name_proper = municipality_name.title()
                        municipality, created = Municipality.objects.get_or_create(province=province, name=municipality_name_proper)
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'    Added Municipality: {municipality.name}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'    Found existing Municipality: {municipality.name}'))

                        for barangay_name in municipality_data['barangay_list']:
                            barangay_name_proper = barangay_name.title()
                            barangay, created = Barangay.objects.get_or_create(municipality=municipality, name=barangay_name_proper)
                            if created:
                                self.stdout.write(self.style.SUCCESS(f'      Added Barangay: {barangay.name}'))
                            else:
                                self.stdout.write(self.style.WARNING(f'      Found existing Barangay: {barangay.name}'))

        self.stdout.write(self.style.SUCCESS('Finished loading PH address data in Proper caps!'))
