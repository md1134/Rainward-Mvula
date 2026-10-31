from django.core.management.base import BaseCommand

from risk.models import Area, Schedule

# Approximate centre points. Schedules are PLACEHOLDERS: replace with the real ZESCO / Lusaka Water notices.
AREAS = [
    ("Kanyama", -15.4450, 28.2400, True, "Mon, Wed, Fri 06:00-10:00", "Tue, Thu 18:00-22:00"),
    ("Mtendere", -15.4100, 28.3500, False, "Tue, Thu, Sat 05:00-09:00", "Mon, Wed 18:00-22:00"),
    ("Chawama", -15.4600, 28.2800, True, "Mon, Thu 06:00-11:00", "Wed, Fri 18:00-22:00"),
    ("Matero", -15.3850, 28.2400, False, "Wed, Sat 06:00-10:00", "Tue, Fri 18:00-22:00"),
    ("Chilenje", -15.4500, 28.3100, False, "Tue, Fri 06:00-10:00", "Mon, Thu 18:00-22:00"),
]


class Command(BaseCommand):
    help = "Seed Lusaka compounds with placeholder schedules"

    def handle(self, *args, **opts):
        for name, lat, lon, prone, water, power in AREAS:
            a, _ = Area.objects.update_or_create(name=name, defaults=dict(latitude=lat, longitude=lon, flood_prone=prone))
            Schedule.objects.update_or_create(area=a, kind="water", defaults={"window": water})
            Schedule.objects.update_or_create(area=a, kind="power", defaults={"window": power})
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(AREAS)} areas"))
