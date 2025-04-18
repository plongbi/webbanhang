import pandas as pd
import requests
from django.core.management.base import BaseCommand
from django.core.files import File
from io import BytesIO
from app.models import Product, Category  # Import cả Category

class Command(BaseCommand):
    help = 'Import products from Excel into Django database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        try:
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip().str.title()

            for index, row in df.iterrows():
                try:
                    name = str(row.get('Name', '')).strip()
                    price = row.get('Price', 0)
                    description = str(row.get('Description', '')).strip()
                    detail = str(row.get('Detail', '')).strip()
                    image_url = str(row.get('Image', '')).strip()
                    category_names = str(row.get('Category', '')).split(',')

                    media_urls = {
                        'media1': str(row.get('Media1', '')).strip(),
                        'media2': str(row.get('Media2', '')).strip(),
                        'media3': str(row.get('Media3', '')).strip()
                    }

                    # 🔒 Kiểm tra nếu sản phẩm đã tồn tại
                    if Product.objects.filter(name=name).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️ Sản phẩm '{name}' đã tồn tại, bỏ qua."))
                        continue

                    # 🆕 Tạo mới sản phẩm
                    product = Product(
                        name=name,
                        price=int(price),
                        detail=detail,
                        description=description,
                    )

                    # Xử lý ảnh chính
                    if image_url and image_url.startswith(('http://', 'https://')):
                        try:
                            response = requests.get(image_url, timeout=10)
                            response.raise_for_status()
                            image_name = image_url.split('/')[-1]
                            product.image.save(
                                image_name,
                                File(BytesIO(response.content)),
                                save=False
                            )
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(
                                f"⚠️ Không thể tải ảnh chính từ {image_url} cho sản phẩm {name}: {str(e)}"
                            ))

                    # Xử lý ảnh phụ (media1, media2, media3)
                    for field_name, media_url in media_urls.items():
                        if media_url and media_url.startswith(('http://', 'https://')):
                            try:
                                response = requests.get(media_url, timeout=10)
                                response.raise_for_status()
                                image_name = media_url.split('/')[-1]
                                getattr(product, field_name).save(
                                    image_name,
                                    File(BytesIO(response.content)),
                                    save=False
                                )
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(
                                    f"⚠️ Không thể tải {field_name} từ {media_url} cho sản phẩm {name}: {str(e)}"
                                ))

                    product.save()

                    # Xử lý category
                    categories = []
                    for cat_name in category_names:
                        cat_name = cat_name.strip()
                        if not cat_name:
                            continue
                        cat_obj, _ = Category.objects.get_or_create(
                            name=cat_name,
                            defaults={'slug': cat_name.lower().replace(' ', '-')}
                        )
                        categories.append(cat_obj)

                    product.category.set(categories)

                    self.stdout.write(self.style.SUCCESS(f"✅ Đã import sản phẩm: {product.name}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Lỗi dòng {index + 2}: {str(e)}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("❌ Không tìm thấy file Excel!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Lỗi hệ thống: {str(e)}"))
        finally:
            self.stdout.write(self.style.SUCCESS("✅ Kết thúc quá trình import"))
