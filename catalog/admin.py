from django.contrib import admin
from .models import Brand, Smartphone, AIPriceRecommendation, ContactMessage


admin.site.register(Brand)


@admin.register(Smartphone)
class SmartphoneAdmin(admin.ModelAdmin):
    list_display = (
        'brand', 
        'model_name', 
        'release_date', 
        'ram', 
        'storage', 
        'battery_capacity', 
        'antutu_score', 
        'uzb_price'
    )
    
    list_display_links = ('brand', 'model_name')
    list_filter = ('brand', 'release_date', 'created_at')
    search_fields = ('model_name', 'cpu', 'gpu', 'description', 'brand__name')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('brand', 'model_name', 'release_date', 'description')
        }),
        ('Texnik Xarakteristikalar', {
            'fields': ('cpu', 'gpu', 'ram', 'storage', 'antutu_score'),
            'classes': ('collapse',),
        }),
        ('Kamera va Korpus', {
            'fields': ('camera_mp', 'old_camera', 'battery_capacity', 'body_material', 'special_features'),
            'classes': ('collapse',),
        }),
        ('Narxlar va Qo\'shimcha', {
            'fields': ('global_price', 'uzb_price', 'user_feedback', 'image_url'),
        }),
    )
    
    date_hierarchy = 'release_date'
    ordering = ('-created_at',)


@admin.register(AIPriceRecommendation)
class AIPriceRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'brand_name', 
        'model_name', 
        'usage_goal', 
        'max_price', 
        'global_price', 
        'antutu_score', 
        'created_at'
    )
    
    list_display_links = ('brand_name', 'model_name')
    list_filter = ('brand_name', 'usage_goal', 'created_at')
    search_fields = ('brand_name', 'model_name', 'cpu', 'gpu', 'description')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('brand_name', 'model_name', 'usage_goal', 'description')
        }),
        ('Texnik Xarakteristikalar', {
            'fields': ('cpu', 'gpu', 'ram', 'antutu_score'),
            'classes': ('collapse',),
        }),
        ('Narxlar va Multimedia', {
            'fields': ('max_price', 'global_price', 'image_url'),
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)




@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('first_name', 'last_name', 'email', 'subject', 'created_at', 'is_read')
    list_filter   = ('is_read',)
    search_fields = ('first_name', 'email', 'subject')
    readonly_fields = ('first_name', 'last_name', 'email', 'subject', 'message', 'created_at')