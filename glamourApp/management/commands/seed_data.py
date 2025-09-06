from django.core.management.base import BaseCommand
from django.core.files import File
from glamourApp.models import (
    Category,
    SubCategory,
    Product,
    ProductSize,
    ProductColor,
    ProductImage,
)
import random
from pathlib import Path
from django.conf import settings
import os


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Clear existing data
        self.stdout.write("Clearing existing data...")
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        SubCategory.objects.all().delete()
        Category.objects.all().delete()
        ProductSize.objects.all().delete()
        ProductColor.objects.all().delete()

        # Create categories
        categories_data = [
            {
                "name": "Men",
                "description": "All men's clothing and accessories",
                "subcategories": ["Shirts", "Pants", "Shoes", "Accessories"],
            },
            {
                "name": "Women",
                "description": "All women's clothing and accessories",
                "subcategories": ["Dresses", "Tops", "Skirts", "Shoes", "Accessories"],
            },
            {
                "name": "Kids",
                "description": "All children's clothing and accessories",
                "subcategories": ["Boys", "Girls", "Shoes", "Accessories"],
            },
            {
                "name": "Unisex",
                "description": "Clothing and accessories for everyone",
                "subcategories": ["T-Shirts", "Hoodies", "Sneakers", "Accessories"],
            },
        ]

        # Create colors
        colors = [
            "Red",
            "Blue",
            "Green",
            "Black",
            "White",
            "Gray",
            "Navy",
            "Pink",
            "Purple",
            "Yellow",
        ]
        color_objects = []
        for color_name in colors:
            color = ProductColor.objects.create(color=color_name)
            color_objects.append(color)

        # Define sizes
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]

        # Sample product details
        product_templates = [
            {
                "name_template": "{} Fashion {} {}",
                "description_template": "A stylish {} {} perfect for any occasion. Made with premium materials for comfort and durability.",
                "price_usd": lambda: random.uniform(29.99, 199.99),
                "items": ["Classic", "Modern", "Trendy", "Casual", "Elegant"],
            }
        ]

        for category_data in categories_data:
            # Create category
            category = Category.objects.create(
                name=category_data["name"], description=category_data["description"]
            )

            # Create subcategories
            for subcat_name in category_data["subcategories"]:
                subcategory = SubCategory.objects.create(
                    name=subcat_name, category=category
                )

                # Create products for each subcategory
                for _ in range(4):  # 4 products per subcategory
                    template = random.choice(product_templates)
                    style = random.choice(template["items"])

                    price_usd = round(template["price_usd"](), 2)
                    price_ngn = round(price_usd * 800, 2)  # Assuming 1 USD = 800 NGN
                    price_eur = round(price_usd * 0.85, 2)  # Assuming 1 USD = 0.85 EUR

                    product = Product.objects.create(
                        name=template["name_template"].format(
                            style, category.name, subcat_name
                        ),
                        description=template["description_template"].format(
                            style.lower(), subcat_name.lower()
                        ),
                        category=category,
                        sub_category=subcategory,
                        price_usd=price_usd,
                        price_ngn=price_ngn,
                        price_eur=price_eur,
                    )

                    # Add random sizes and colors
                    for size_name in random.sample(
                        sizes, k=random.randint(3, len(sizes))
                    ):
                        size = ProductSize.objects.create(
                            name=size_name, product=product
                        )
                        product.sizes.add(size)

                    for color in random.sample(
                        color_objects, k=random.randint(3, len(color_objects))
                    ):
                        product.colors.add(color)

                    # Create dummy product images (you should replace these with real images)
                    media_root = settings.MEDIA_ROOT
                    default_image_path = os.path.join(
                        settings.BASE_DIR, "static", "img", "default-product.png"
                    )

                    if os.path.exists(default_image_path):
                        for i in range(3):  # 3 images per product
                            with open(default_image_path, "rb") as img_file:
                                image = ProductImage.objects.create(product=product)
                                image_name = f"{product.name.lower().replace(' ', '-')}-{i+1}.jpg"
                                image.image.save(image_name, File(img_file), save=True)
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Default image not found at {default_image_path}. Skipping image creation."
                            )
                        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))
