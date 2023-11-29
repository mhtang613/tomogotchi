import os
from django.core.management.base import BaseCommand
from django.core.files import File
from tomogotchi.models import *

class Command(BaseCommand):
    help = "Load static data (shop catalog) into the databases"

    def handle(self, *args, **options):
        # loop through food folder
        files_dir = os.path.join('tomogotchi','static','images','food')

        for file in os.listdir(files_dir):
            if file.endswith('.png') or file.endswith('.gif'):
                file_path = os.path.join(files_dir, file)
                if not Items.objects.filter(name__iexact=file).exists():
                    with open(file_path, 'rb') as file_content:
                        file_instance = File(file_content)
                        file_instance.name = file
                        item = Items(picture=file_instance, 
                                     is_furniture=False, 
                                     is_big=False, 
                                     content_type="image/png",
                                     hitboxX = 0,
                                     hitboxY = 0)
                        # Add hunger and price for food items
                        file_name = (file.lower())[:-4]
                        words = file_name.split('_')
                        name = words[0]
                        hunger = int(words[1])
                        price = int(words[2])
                        item.name = name
                        item.price = price
                        item.hunger = hunger                       
                            
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Loaded food: {file}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Skipped food: {file}'))
    
        # loop through furniture folder
        files_dir2 = os.path.join('tomogotchi','static','images','furniture')

        for file in os.listdir(files_dir2):
            if file.endswith('.png') or file.endswith('.gif'):
                file_path = os.path.join(files_dir2, file)
                if not Items.objects.filter(name__iexact=file).exists():
                    with open(file_path, 'rb') as file_content:
                        file_instance = File(file_content)
                        file_instance.name = file
                        item = Items(picture=file_instance, 
                                     is_furniture=True, 
                                     content_type="image/png",
                                     hunger=0)
                        # Add hunger and price for food items
                        file_name = (file.lower())[:-4]
                        words = file_name.split('_')
                        name = words[0]
                        width = int(words[1])
                        height = int(words[2])
                        price = int(words[3])
                        item.name = name
                        item.hitboxX = width
                        item.hitboxY = height
                        item.price = price
                        item.is_big = True if (width * height > 1) else False
                            
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f'Loaded furniture: {file}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Skipped furniture: {file}'))

