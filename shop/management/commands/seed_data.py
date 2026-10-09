from django.core.management.base import BaseCommand
from shop.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with sample products'

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

        for p in products:
            # We use update_or_create to allow running the command safely multiple times
            product, created = Product.objects.update_or_create(
                slug=p['slug'],
                defaults=p
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {p['name']}"))
            else:
                self.stdout.write(f"Updated product: {p['name']}")
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded sample products!'))
