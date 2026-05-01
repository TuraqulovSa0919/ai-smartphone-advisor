from django.db import models
from django.utils import timezone
from datetime import timedelta

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class Smartphone(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=250)
    release_date = models.DateField(null=True, blank=True)
    cpu = models.CharField(max_length=500, null=True, blank=True)
    gpu = models.CharField(max_length=500, null=True, blank=True)
    ram = models.CharField(max_length=200)
    storage = models.CharField(max_length=200)
    camera_mp = models.CharField(max_length=400)
    old_camera = models.CharField(max_length=400, null=True, blank=True)
    battery_capacity = models.IntegerField()
    antutu_score = models.IntegerField(default=0)
    body_material = models.CharField(max_length=600, null=True, blank=True) 
    special_features = models.TextField(null=True, blank=True) 
    global_price = models.CharField(max_length=600, null=True, blank=True)
    uzb_price = models.CharField(max_length=600, null=True, blank=True)
    
    user_feedback = models.JSONField(null=True, blank=True) 
    description = models.TextField() 
    
    image_url = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return f"{self.brand.name} {self.model_name}"


class AIPriceRecommendation(models.Model):
    max_price = models.FloatField()
    usage_goal = models.CharField(max_length=50)
    brand_name = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    cpu = models.CharField(max_length=255, null=True, blank=True)
    gpu = models.CharField(max_length=255, null=True, blank=True)
    ram = models.CharField(max_length=50, null=True, blank=True)
    antutu_score = models.IntegerField(null=True, blank=True)
    global_price = models.FloatField(null=True, blank=True)
    description = models.TextField() 
    image_url = models.URLField(max_length=500, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created_at >= timezone.now() - timedelta(days=30)
    
    def __str__(self): return f"{self.brand_name} {self.model_name}"