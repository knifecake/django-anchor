from django.core.management.base import BaseCommand
from django.utils import timezone

from anchor.models import Blob


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Dry run the command"
        )
        parser.add_argument(
            "--until",
            type=lambda x: timezone.datetime.fromisoformat(x),
            help="Only purge blobs created before this date",
        )

    def handle(self, *args, **kwargs):
        blobs = Blob.objects
        if kwargs["until"]:
            blobs = blobs.filter(
                created_at__lt=timezone.make_aware(
                    kwargs["until"], timezone.get_current_timezone()
                )
            )
        blobs = blobs.unattached()

        self.stdout.write(f"Purging {blobs.count()} unattached blobs")

        for blob in blobs:
            if not kwargs["dry_run"]:
                blob.purge()
                blob.delete()
            else:
                self.stdout.write(f"Would delete {blob.id}")
