from django.core.management.base import BaseCommand
import boto3
import os
from record_management.models import Pet
from django.contrib.auth import authenticate
from getpass import getpass

class Command(BaseCommand):
    help = 'Prints matching images between S3 and Django DB.'

    def handle(self, *args, **options):
        try:
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

            # Find matching files
            matching_files = all_s3_files.intersection(all_django_files)
            
            for file_path in matching_files:
                self.stdout.write(f"Matching file: {file_path}")

            self.stdout.write(self.style.SUCCESS(f"Found {len(matching_files)} matching files."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))