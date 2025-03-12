import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = 'Import users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f"File '{csv_file}' not found"))
            return

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                print(f"Processing row: {row}")  # Debugging output

                if User.objects.filter(username=row['username']).exists():
                    self.stdout.write(self.style.WARNING(f"User {row['username']} already exists. Skipping..."))
                    continue

                user = User(
                    username=row['username'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    is_staff=bool(int(row['is_staff'])),
                    is_active=bool(int(row['is_active'])),
                    is_superuser=bool(int(row['is_superuser'])),
                )

                user.set_password(row['password'] or get_random_string())  # Hash password
                user.save()

                self.stdout.write(self.style.SUCCESS(f"User {user.username} created successfully."))

        self.stdout.write(self.style.SUCCESS("Import complete."))

