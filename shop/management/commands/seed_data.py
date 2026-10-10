import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from shop.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with sample products safely'

    def handle(self, *args, **kwargs):
        products = [
            {'name': 'Laptop Promax', 'slug': 'laptop-promax', 'description': 'A high performance laptop for developers and creatives.', 'category': 'Electronics', 'price': '1299.99', 'stock': 10},
            {'name': 'Wireless Mouse', 'slug': 'wireless-mouse', 'description': 'Ergonomic wireless mouse with precision tracking.', 'category': 'Electronics', 'price': '25.50', 'stock': 50},
            {'name': 'Mechanical Keyboard', 'slug': 'mechanical-keyboard', 'description': 'RGB mechanical keyboard with tactile switches.', 'category': 'Electronics', 'price': '89.99', 'stock': 20},
            {'name': 'Ceramic Coffee Mug', 'slug': 'coffee-mug', 'description': 'Minimalist ceramic coffee mug. 12oz capacity.', 'category': 'Home', 'price': '12.00', 'stock': 100},
            {'name': 'LED Desk Lamp', 'slug': 'desk-lamp', 'description': 'Adjustable LED desk lamp with multiple color temperatures.', 'category': 'Home', 'price': '35.00', 'stock': 15},
            {'name': 'Noise Cancelling Headphones', 'slug': 'headphones', 'description': 'Over-ear wireless headphones with active noise cancellation.', 'category': 'Electronics', 'price': '199.99', 'stock': 25},
            {'name': 'Classic T-Shirt', 'slug': 'classic-tshirt', 'description': '100% cotton everyday comfortable t-shirt.', 'category': 'Apparel', 'price': '19.99', 'stock': 200},
            {'name': 'Out of Stock Item', 'slug': 'out-of-stock', 'description': 'This item is currently out of stock.', 'category': 'Home', 'price': '49.99', 'stock': 0},
        ]

        seed_images_dir = os.path.join(settings.BASE_DIR, 'shop', 'static', 'shop', 'images', 'seeds')

        for p in products:
            # We use get_or_create to preserve existing prices, stock, and descriptions
            product, created = Product.objects.get_or_create(
                slug=p['slug'],
                defaults=p
            )
            
            # Idempotently add missing images without overwriting administrator uploads
            if not product.image or not product.image.storage.exists(product.image.name):
                # Try PNG first, then SVG
                found_path = None
                found_ext = None
                for ext in ['.png', '.svg']:
                    test_filename = f"{p['slug']}{ext}"
                    test_path = os.path.join(seed_images_dir, test_filename)
                    if os.path.exists(test_path):
                        found_path = test_path
                        found_ext = ext
                        break
                
                if found_path:
                    image_filename = f"{p['slug']}{found_ext}"
                    with open(found_path, 'rb') as fp:
                        product.image.save(image_filename, File(fp), save=True)
                        self.stdout.write(f"Attached image for {p['name']}")
                else:
                    pass # Silently skip missing seed images, they will use fallback in UI

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {p['name']}"))
            else:
                self.stdout.write(f"Product {p['name']} already exists, skipped overwriting data.")
        
        self.stdout.write(self.style.SUCCESS('Successfully verified sample products!'))
