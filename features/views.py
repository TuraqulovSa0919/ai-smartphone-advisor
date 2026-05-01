from django.shortcuts import render
from .models import CameraPhone, GamingSmartphones, Performance


def camera_phones_view(request):
    phones = CameraPhone.objects.all().order_by('camera_rank')
    return render(request, 'features/camera_phones.html', {'camera_phones': phones})


def gaming_phones_view(request):
    all_gaming_phones = GamingSmartphones.objects.all().order_by('-antutu_v11_score')
    context = {
        'phones': all_gaming_phones,
    }
    return render(request, 'features/gaming_phones.html', context)

def performance_view(request):

    top_phones = Performance.objects.all().order_by('-antutu_score')
    
    context = {
        'performance_phones': top_phones,
        'title': "AnTuTu Global Performance Top 30"
    }
    return render(request, 'features/performance.html', context)