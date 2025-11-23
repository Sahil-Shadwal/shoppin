from django.core.management.base import BaseCommand
from search.models import ScrapedImage

class Command(BaseCommand):
    help = 'Deletes all scraped images from the database'

    def handle(self, *args, **options):
        count = ScrapedImage.objects.count()
        self.stdout.write(f'Deleting {count} scraped images...')
        ScrapedImage.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} scraped images.'))
