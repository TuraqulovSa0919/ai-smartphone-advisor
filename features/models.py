from django.db import models


class CameraPhone(models.Model):
    img_url = models.URLField(max_length=500, null=True, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    cpu = models.CharField(max_length=100)
    gpu = models.CharField(max_length=100)
    camera = models.TextField()
    video = models.CharField(max_length=100)
    body = models.CharField(max_length=100)
    antutu = models.CharField(max_length=50)
    battery = models.CharField(max_length=50, null=True, blank=True)
    ai_comment = models.TextField()
    camera_rank = models.PositiveIntegerField(default=0, help_text="Kamera sifati bo'yicha o'rni (1 - eng zo'ri)")
    class Meta:
        ordering = ['camera_rank'] 
        
    def __str__(self):
        return f"#{self.camera_rank} - {self.brand} {self.model}"


class GamingSmartphones(models.Model):
    SEGMENT_CHOICES = (
        ('hardcore', 'Hardcore Gaming (Mutlaq Yetakchilar)'),
        ('flagship', 'Flagship (Yuqori Unumdor Flagmanlar)'),
        ('premium', 'Premium & Foldable (Buklanuvchan va Premium)'),
        ('value', 'Value for Money (Narx/Sifat nisbati)'),
    )

    image_url = models.URLField(max_length=500, verbose_name="Rasm URL manzili")
    antutu_v11_score = models.IntegerField(verbose_name="AnTuTu v11 Real Vaqt Balli")
    brand = models.CharField(max_length=50, verbose_name="Brend")
    device_model = models.CharField(max_length=100, verbose_name="Smartfon Modeli")
    cpu = models.CharField(max_length=100, verbose_name="Protsessor (CPU)")
    gpu = models.CharField(max_length=100, verbose_name="Video tezlatgich (GPU)")
    camera = models.CharField(max_length=255, verbose_name="Kamera xususiyatlari")
    body_material = models.CharField(max_length=255, verbose_name="Korpus va Material")
    additional_features = models.TextField(verbose_name="Qo'shimcha Imkoniyatlar")
    segment = models.CharField(max_length=50, choices=SEGMENT_CHOICES, verbose_name="Smartfon Segmenti")
    ai_summary = models.TextField(verbose_name="AI Xulosasi (Tahlil)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Bazaga qo'shilgan vaqt")

    def __str__(self):
        return f"{self.brand} {self.device_model} - {self.antutu_v11_score} ball"

    class Meta:
        verbose_name = "Gaming Smartphone"
        verbose_name_plural = "Gaming Smartphones"
        ordering = ['-antutu_v11_score'] 


class Performance(models.Model):
    rank = models.PositiveIntegerField(unique=True)
    img_url = models.URLField(max_length=500, null=True, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    antutu_score = models.IntegerField()
    cpu = models.CharField(max_length=100)
    gpu = models.CharField(max_length=100)
    ram = models.CharField(max_length=50)
    camera = models.TextField(null=True, blank=True)
    battery = models.CharField(max_length=50, null=True, blank=True)
    body = models.CharField(max_length=100, null=True, blank=True)
    ai_comment = models.TextField(null=True, blank=True)
    user_feedback = models.TextField(null=True, blank=True, help_text="Foydalanuvchilar fikri")

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} - {self.brand} {self.model}"
    
