from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.

# Customer model for which user is a OneToOneField with Django's built-in User model
# This is because there is only one customer per one user
class Customer(models.Model):
    user = models.OneToOneField(User,null=True, blank=True,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20,null=True)
    last_name = models.CharField(max_length=20,null=True)
    email = models.CharField(max_length=200,null=True)

    def __str__(self):
        return f"{self.first_name}{self.last_name}"

# Product model
class Product(models.Model):
    name = models.CharField(max_length=200,null=True)
    price = models.DecimalField(max_digits=7,decimal_places=2)
    image = models.ImageField(null=True,blank=True)
    digital = models.BooleanField(default=False)
    description = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url=self.image.url
        except:
            url = ''
        return url

    def get_absolute_url(self):
        return reverse('product_detail',kwargs={'id':self.id})


# Order model
class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True,blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100,null=True)

    def __str__(self):
        return str(self.id)

    @property
    # This function calculates the sum total price of all the order items the cart
    def get_cart_total(self):
        # Firstly, we get all the order items in the cart
        orderitems = self.orderitem_set.all()
        # We loop through each order item while
        # The get_total funciton calculates the total price per order item (which is summed up)
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        # Firstly, we get all the order items in the cart
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    # This function checks if we have any physical items in the cart
    @property
    def shipping(self):
        shipping = False
        orderitems=self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

# The object for the items that are added to an Order - before the Order is placed
# Consider that an order is a the cart and OrderItem is an item within the cart
class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True,blank=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL, null=True,blank=True)
    quantity = models.IntegerField(default=0,null=True,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # This function gets the total price per order item in the cart
    # It gets returned to the cart.html template via the items variable in the context dictionary
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

# Shipping Address model
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True,blank=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL, null=True,blank=True)
    address = models.CharField(max_length=200,null=True)
    city = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    zipcode = models.CharField(max_length=200,null=True)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
