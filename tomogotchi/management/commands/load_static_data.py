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
                is_big = True if "big" in file.lower() else False
                
                file_path = os.path.join(files_dir, file)

                if not Items.objects.filter(name__iexact=file).exists():
                    with open(file_path, 'rb') as file_content:
                        file_instance = File(file_content)
                        file_instance.name = file
                        item = Items(name=file, 
                                     picture=file_instance, 
                                     is_furniture=is_furniture, 
                                     is_big=is_big, 
                                     content_type="image/png")
                        # Manually add width, height, and price for furniture items
                        if is_furniture:
                            if "bookshelf1" in file.lower():
                                item.hitboxX = 3
                                item.hitboxY = 4
                                item.price = 50
                            elif "clock1" in file.lower():
                                item.hitboxX = 1
                                item.hitboxY = 3
                                item.price = 30
                            elif "plant1" in file.lower():
                                item.hitboxX = 1
                                item.hitboxY = 2
                                item.price = 10
                            elif "table1" in file.lower():
                                item.hitboxX = 2
                                item.hitboxY = 3
                                item.price = 40
                        # Manually add price for food items
                        else:
                            if "cake" in file.lower():
                                item.price = 15
                            elif "burger" in file.lower():
                                item.price = 8
                            
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Loaded {file}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Skipped {file}'))

