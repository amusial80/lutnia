import csv
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

csv_file = "users.csv"  # Change this to your file path

with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        if User.objects.filter(username=row["username"]).exists():
            print(f"User {row['username']} already exists. Skipping...")
            continue

        user = User(
            username=row["username"],
            email=row["email"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            is_staff=bool(int(row["is_staff"])),
            is_active=bool(int(row["is_active"])),
            is_superuser=bool(int(row["is_superuser"])),
        )

        user.set_password(row["password"])  # Hash the password!
        user.save()

        print(f"User {user.username} created successfully!")

print("Import complete.")
