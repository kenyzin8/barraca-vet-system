from django.core.management.base import BaseCommand
import boto3
import os
from record_management.models import Pet, LabResult
from django.contrib.auth import authenticate
from getpass import getpass

class Command(BaseCommand):
    help = 'Prints matching images between S3 and Django DB.'

    def get_django_files(self, model, image_field_name):
        return set([getattr(instance, image_field_name).name for instance in model.objects.all() if getattr(instance, image_field_name)])

    def handle(self, *args, **options):
        try:
            self.stdout.write('-' * 80)
            username = input("Please enter your username: ")
            password = getpass("Please enter your password: ")
            
            user = authenticate(username=username, password=password)

            if user is None or not user.is_superuser:
                self.stdout.write(self.style.ERROR("Authentication failed or user is not a superadmin. Exiting..."))
                return

            session = boto3.Session(
                aws_access_key_id=os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('BUCKETEER_AWS_REGION')
            )

            s3 = session.resource('s3')
            bucket = s3.Bucket(os.getenv('BUCKETEER_BUCKET_NAME'))

            all_s3_files = set([obj.key for obj in bucket.objects.filter(Prefix='public/images/')])
            
            pet_files = self.get_django_files(Pet, 'picture')
            lab_result_files = self.get_django_files(LabResult, 'result_image')
            all_django_files = pet_files.union(lab_result_files)

            matching_files = all_s3_files.intersection(all_django_files)
            unused_files = all_s3_files - all_django_files

            self.stdout.write('-' * 80)
            for pet in Pet.objects.all():
                if pet.picture.name in matching_files:
                    self.stdout.write(f"Matching file for pet {pet.name} (ID: {pet.id}): {pet.picture.name}")
            
            for lab_result in LabResult.objects.all():
                if lab_result.result_image.name in matching_files:
                    self.stdout.write(f"Matching file for lab result {lab_result.result_name} (ID: {lab_result.id}): {lab_result.result_image.name}")

            self.stdout.write(self.style.SUCCESS(f"Found {len(matching_files)} used files."))

            for file_path in unused_files:
                self.stdout.write(f"Unused file: {file_path}")
            
            self.stdout.write(self.style.SUCCESS(f"Found {len(unused_files)} unused files."))
            self.stdout.write('-' * 80)
            self.stdout.write(self.style.NOTICE(f"Use 'python manage.py cleanunusedimages' to delete unused files."))
            self.stdout.write('-' * 80)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))