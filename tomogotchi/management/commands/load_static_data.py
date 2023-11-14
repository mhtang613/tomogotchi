import os
from django.core.management.base import BaseCommand
from django.core.files import File
from tomogotchi.models import *

class Command(BaseCommand):
    help = "Load static data (shop catalog) into the databases"

    def handle(self, *args, **options):
        files_dir = os.path.join('tomogotchi','static','images','items')

        
        for file in os.listdir(files_dir):
            if file.endswith('.png') or file.endswith('.gif'):
                is_furniture = True if "furniture" in file.lower() else False
                file_path = os.path.join(files_dir, file)

                if not Items.objects.filter(name__iexact=file).exists():
                    with open(file_path, 'rb') as file_content:
                        file_instance = File(file_content)
                        file_instance.name = file
                        item = Items(name=file, picture=file_instance, is_furniture=is_furniture,content_type="image/png")
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Loaded {file}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Skipped {file}'))
