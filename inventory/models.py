from django.db import models
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator, DecimalValidator
from django.contrib.contenttypes.models import ContentType

from core.models import Notification

class ProductType(models.Model):
    name = models.CharField(max_length=50)
    product_type_description = models.TextField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk:
            orig = ProductType.objects.get(pk=self.pk)
            if orig.name == "Medicines" and self.name != "Medicines":
                raise ValueError("The name of the 'Medicines' Product Type cannot be changed.")
        super(ProductType, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.name == "Medicines":
            raise ValueError("The 'Medicines' Product Type cannot be deleted.")
        super(ProductType, self).delete(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Type"
        verbose_name_plural = "Product Types"


class Product(models.Model):

    PRODUCT_FORM_LIST = (
        ('', 'Select Form'),
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('granule', 'Granule'),
        ('chew', 'Chewable'),
        ('pellet', 'Pellet'),
        ('injection', 'Injection'),
        ('liquid', 'Liquid'),
        ('feed_additive', 'Feed Additive'),
        ('oral_solution', 'Oral Solution'),
        ('ear_drop', 'Ear Drop'),
        ('spot-on', 'Spot-On Treatment'),
        ('gel', 'Gel'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('lotion', 'Lotion'),
        ('suspension', 'Suspension'),
        ('drop', 'Drop'),
        ('spray', 'Spray'),
        ('powder', 'Powder'),
        ('paste', 'Paste'),
        ('bolus', 'Bolus'),
        ('other', 'Other'),
    )

    VOLUME_UNIT_CHOICES = (
        ('', 'Select Unit'),
        ('g', 'Gram (g)'),
        ('kg', 'Kilogram (kg)'),
        ('mL', 'Milliliter (mL)'),
        ('L', 'Liter (L)'),
        ('piece', 'Piece'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('set', 'Set'),
    )

    product_name = models.CharField(max_length=255)
    quantity_on_stock = models.DecimalField(default=1.00, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    volume = models.DecimalField(default=1.00, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    volume_unit = models.CharField(max_length=20, choices=VOLUME_UNIT_CHOICES, default='piece')
    form = models.CharField(max_length=20, choices=PRODUCT_FORM_LIST, default='other')
    type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
    batch_number = models.CharField(max_length=255, default="-")
    manufacturer = models.CharField(max_length=255, default="-")
    manufacturing_date = models.DateField()
    expiration_date = models.DateField()
    critical_level = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField(max_length=255, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    changes_log = models.JSONField(default=dict, blank=True)
    has_new_batch = models.BooleanField(default=False)
    old_batch = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_name}"

    def is_product_critical(self):
        if not self.has_new_batch:
            return self.quantity_on_stock <= self.critical_level
        return False

    def is_product_expired(self):
        return self.expiration_date < datetime.date.today()

    def is_product_out_of_stock(self):
        return self.quantity_on_stock == 0

    def get_dosage_unit(self, for_dosage=False):
        liquid_forms = ['syrup', 'liquid', 'oral_solution', 'suspension', 'ear_drop', 'gel', 'cream', 'ointment', 'lotion', 'feed_additive', 'drop', 'spray']
        
        if self.form in liquid_forms:
            return 'mL'
        else:
            if for_dosage and self.dosage != '1':
                return self.form + 's'
            return self.form

    def create_or_delete_notification(self, condition, notification_type, message):
        content_type = ContentType.objects.get_for_model(Product)
        if condition:
            notification, created = Notification.objects.get_or_create(
                text=message,
                content_type=content_type,
                object_id=self.id,
                notification_type=notification_type,
                defaults={'is_active': True}
            )
            if not created and not notification.is_active:
                notification.is_active = True
                notification.save()
        else:
            Notification.objects.filter(
                content_type=content_type, 
                object_id=self.id,
                notification_type=notification_type
            ).update(is_active=False)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Product.objects.get(pk=self.pk)
            changes = {}

            if orig.product_name != self.product_name:
                changes['product_name'] = [orig.product_name, self.product_name]
            if orig.quantity_on_stock != self.quantity_on_stock:
                changes['quantity_on_stock'] = [str(orig.quantity_on_stock), str(self.quantity_on_stock)]
            if orig.type != self.volume:
                changes['volume'] = [str(orig.volume), str(self.volume)]
            if orig.form != self.form:
                changes['form'] = [orig.form, self.form]
            if orig.type != self.type:
                changes['type'] = [str(orig.type), str(self.type)]
            if orig.manufacturing_date != self.manufacturing_date:
                changes['manufacturing_date'] = [str(orig.manufacturing_date), str(self.manufacturing_date)]
            if orig.expiration_date != self.expiration_date:
                changes['expiration_date'] = [str(orig.expiration_date), str(self.expiration_date)]
            if orig.critical_level != self.critical_level:
                changes['critical_level'] = [orig.critical_level, self.critical_level]
            if orig.price != self.price:
                changes['price'] = [str(orig.price), str(self.price)]
            if orig.batch_number != self.batch_number:
                changes['batch_number'] = [orig.batch_number, self.batch_number]
            if orig.manufacturer != self.manufacturer:
                changes['manufacturer'] = [orig.manufacturer, self.manufacturer]
            if orig.product_description != self.product_description:
                changes['product_description'] = [orig.product_description, self.product_description]
                
            if changes:
                if self.changes_log:
                    update_id = self.changes_log[-1].get('update_id', 0) + 1
                else:
                    update_id = 1
                    
                changes['update_id'] = update_id
                changes['date'] = datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")

                if self.changes_log:
                    self.changes_log.append(changes)
                else:
                    self.changes_log = [changes]

        super().save(*args, **kwargs)

        if self.active:
            self.create_or_delete_notification(
                self.is_product_critical(),
                Notification.CRITICAL,
                f"Critical Level - {self.product_name}"
            )

            # self.create_or_delete_notification(
            #     self.is_product_out_of_stock(),
            #     Notification.OUT_OF_STOCK,
            #     f"Out of Stock - {self.product_name}"
            # )

            # self.create_or_delete_notification(
            #     self.is_product_expired(),
            #     Notification.EXPIRED,
            #     f"Expired - {self.product_name}"
            # )

# class Product(models.Model):
#     product_name = models.CharField(max_length=255)
#     quantity_on_stock = models.DecimalField(default=1.00, max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
#     type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True)
#     batch_number = models.IntegerField(default=1)
#     manufacturing_date = models.DateField()
#     expiration_date = models.DateField()
#     critical_level = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     date_added = models.DateTimeField(auto_now_add=True)
#     active = models.BooleanField(default=True)

#     previous_version = models.CharField(null=True, blank=True)
#     updated_version = models.CharField(null=True, blank=True)
#     original_product = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

#     changes_log = JSONField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.product_name}"

#     def create_new_version(self, product_name=None, quantity_on_stock=None, type=None, 
#                         manufacturing_date=None, expiration_date=None, critical_level=None, price=None):

#         previous_version = None
#         updated_version = None
#         batch_number = self.batch_number
        
#         if product_name and product_name != self.product_name:
#             previous_version = f"Product Name: {self.product_name}"
#             updated_version = f"Product Name: {product_name}"
#             product_name = product_name
#         else:
#             product_name = self.product_name

#         if quantity_on_stock and quantity_on_stock != self.quantity_on_stock:
#             previous_version = f"Quantity on Stock: {self.quantity_on_stock}"
#             updated_version = f"Quantity on Stock: {quantity_on_stock}"
#             quantity_on_stock = quantity_on_stock
#         else:
#             quantity_on_stock = self.quantity_on_stock

#         if type and type != self.type:
#             previous_version = f"Type: {self.type}"
#             updated_version = f"Type: {type}"
#             type = type
#         else:
#             type = self.type

#         if manufacturing_date and manufacturing_date != self.manufacturing_date:
#             previous_version = f"Manufacturing Date: {self.manufacturing_date}"
#             updated_version = f"Manufacturing Date: {manufacturing_date}"
#             manufacturing_date = manufacturing_date
#         else:
#             manufacturing_date = self.manufacturing_date

#         if expiration_date and expiration_date != self.expiration_date:
#             previous_version = f"Expiration Date: {self.expiration_date}"
#             updated_version = f"Expiration Date: {expiration_date}"
#             expiration_date = expiration_date
#         else:
#             expiration_date = self.expiration_date

#         if critical_level and critical_level != self.critical_level:
#             previous_version = f"Critical Level: {self.critical_level}"
#             updated_version = f"Critical Level: {critical_level}"
#             critical_level = critical_level
#         else:
#             critical_level = self.critical_level

#         if price and price != self.price:
#             #batch_number = self.batch_number + 1
#             previous_version = f"Price: ₱ {self.price}"
#             updated_version = f"Price: ₱ {price}"
#             price = price
#         else:
#             price = self.price

#         self.active = False
#         self.save()

#         new_product = Product.objects.create(
#             product_name=product_name,
#             quantity_on_stock=quantity_on_stock,
#             type=type,
#             batch_number=self.batch_number + 1,
#             manufacturing_date=manufacturing_date,
#             expiration_date=expiration_date,
#             critical_level=critical_level,
#             price=price,
#             active=True,
#             previous_version=previous_version,
#             updated_version=updated_version,
#             original_product=self if self.original_product is None else self.original_product
#         )

#         return new_product

#     def is_product_critical(self):
#         if self.quantity_on_stock <= self.critical_level:
#             return True
#         else:
#             return False

#     def is_product_expired(self):
#         if self.expiration_date < datetime.date.today():
#             return True
#         else:
#             return False

#     def is_product_out_of_stock(self):
#         if self.quantity_on_stock == 0:
#             return True
#         else:
#             return False

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if self.active and self.original_product is not None:
#             content_type = ContentType.objects.get_for_model(Product)

#             if self.is_product_critical():
#                 Notification.objects.get_or_create(
#                     text=f"Critical Level - {self.product_name}",
#                     content_type=content_type,
#                     object_id=self.original_product.id
#                 )
#             else:
#                 Notification.objects.filter(
#                     text=f"Critical Level - {self.product_name}", 
#                     content_type=content_type, 
#                     object_id=self.original_product.id).delete()
                
#             if self.is_product_out_of_stock():
#                 Notification.objects.get_or_create(
#                     text=f"Out of Stock - {self.product_name}",
#                     content_type=content_type,
#                     object_id=self.original_product.id
#                 )
#             else:
#                 Notification.objects.filter(
#                     text=f"Out of Stock - {self.product_name}", 
#                     content_type=content_type, 
#                     object_id=self.original_product.id).delete()

#             if self.is_product_expired():
#                 Notification.objects.get_or_create(
#                     text=f"Expired - {self.product_name}",
#                     content_type=content_type,
#                     object_id=self.original_product.id
#                 )
#             else:
#                 Notification.objects.filter(
#                     text=f"Expired - {self.product_name}", 
#                     content_type=content_type, 
#                     object_id=self.original_product.id).delete()