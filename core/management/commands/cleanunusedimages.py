from django.core.management.base import BaseCommand
import boto3
import os
from record_management.models import Pet
from django.contrib.auth import authenticate
from getpass import getpass

class Command(BaseCommand):
    help = 'Deletes images from S3 that are not referenced in the Django DB.'

    def handle(self, *args, **kwargs):
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
            all_django_files = set([pet.picture.name for pet in Pet.objects.all()])

            files_to_delete = all_s3_files - all_django_files

            self.stdout.write('-' * 80)

            for file_path in files_to_delete:
                bucket.Object(file_path).delete()
                self.stdout.write(f"Deleted {file_path}")

            self.stdout.write(self.style.SUCCESS(f"Deleted {len(files_to_delete)} files from S3."))
            
            self.stdout.write('-' * 80)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
