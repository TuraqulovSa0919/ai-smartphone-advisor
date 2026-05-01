from django.contrib import admin

from .models import CameraPhone, GamingSmartphones, Performance

@admin.register(CameraPhone)
class CameraPhoneAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'cpu', 'gpu', 'camera', 'video', 'body', 'antutu', 'battery')
    search_fields = ('brand', 'model') 
    list_filter = ('brand', 'antutu')
    ordering = ('-antutu',)

@admin.register(GamingSmartphones)
class GamingSmartphonesAdmin(admin.ModelAdmin):
    list_display = ('brand', 'device_model', 'antutu_v11_score', 'segment', 'created_at')
    search_fields = ('brand', 'device_model', 'cpu')
    list_filter = ('segment', 'brand')
    readonly_fields = ('created_at',)

admin.site.register(Performance)

