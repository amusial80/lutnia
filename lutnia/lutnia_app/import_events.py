import csv
import datetime
from django.utils.timezone import make_aware
from lutnia_app.models import Event

csv_file = "events.csv"  # Update the correct path

with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    for row in reader:
        try:
            # Convert start_time and end_time to datetime (and ensure they are timezone-aware)
            start_time = make_aware(datetime.datetime.strptime(row['start_time'], "%Y-%m-%d %H:%M:%S"))
            end_time = make_aware(datetime.datetime.strptime(row['end_time'], "%Y-%m-%d %H:%M:%S"))

            # Check if event already exists
            if Event.objects.filter(start_time=start_time).exists():
                print(f"Event at {row['start_time']} already exists. Skipping...")
                continue

            # Create and save the event
            event = Event(
                place=int(row['place']),  # Convert to integer if needed
                table=row['table'],
                bookingtype=row['bookingtype'],
                end_time=end_time,
                user_id=int(row['user_id']),  # Convert to integer
                start_time=start_time,
                confirmed=bool(row['confirmed']),
            )

            event.save()
            print(f"Event {event.start_time} created successfully!")

        except Exception as e:
            print(f"Error processing row {row}: {e}")

print("Import complete.")
