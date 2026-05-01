import re
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  
from django.contrib import messages 
from .models import Smartphone, Brand, AIPriceRecommendation
from .services import get_phone_ai_analysis, get_budget_recommendation, get_internet_recommendation



def home(request):
    """Bosh sahifa"""
    return render(request, 'home.html')



@login_required(login_url='login')
def model_search(request):
    return render(request, 'model_search.html')

@login_required(login_url='login')
def price_search(request):
    return render(request, 'price_search.html')

@login_required(login_url='login')
def result_model_search(request):
    query = request.GET.get('q', '').strip()
    results = Smartphone.objects.none()
    ai_message = ""

    if query:
        exact_match = Smartphone.objects.filter(model_name__iexact=query)
        if exact_match.exists():
            results = exact_match
            ai_message = exact_match.first().description
        else:
            partial_matches = Smartphone.objects.filter(
                Q(brand__name__icontains=query) | Q(model_name__icontains=query)
            ).distinct()

            if partial_matches.exists():
                sorted_list = sorted(partial_matches, key=lambda x: len(x.model_name))
                best_phone_id = sorted_list[0].id
                results = Smartphone.objects.filter(id=best_phone_id)
                ai_message = sorted_list[0].description
            else:
                all_brands = list(Brand.objects.values_list('name', flat=True))
                data = get_phone_ai_analysis(query, all_brands)
                
                if data:
                    brand_name = data.get('brand_name', '').strip()
                    brand_obj = Brand.objects.filter(name__iexact=brand_name).first()
                    if not brand_obj:
                        brand_obj = Brand.objects.filter(name__icontains=brand_name[:3]).first()

                    if brand_obj:
                        def clean_to_int(value, default):
                            if not value: return default
                            cleaned = re.sub(r'\D', '', str(value))
                            return int(cleaned) if cleaned else default

                        new_phone, created = Smartphone.objects.get_or_create(
                            brand=brand_obj,
                            model_name=data.get('model_name', query),
                            defaults={
                                'cpu': data.get('cpu'),
                                'gpu': data.get('gpu'),
                                'ram': data.get('ram', '8 GB'),
                                'storage': data.get('storage', '128 GB'),
                                'camera_mp': data.get('camera', '50MP'),
                                'battery_capacity': clean_to_int(data.get('battery'), 5000),
                                'antutu_score': clean_to_int(data.get('antutu'), 0),
                                'description': data.get('full_analysis', ''),
                                'image_url': data.get('image_url')
                            }
                        )
                        results = Smartphone.objects.filter(id=new_phone.id)
                        ai_message = new_phone.description

    return render(request, 'result_model_search.html', {
        'query': query,
        'results': results,
        'ai_message': ai_message
    })

@login_required(login_url='login')
def result_price_search(request):
    max_price = request.GET.get('max_price', 1000)
    usage = request.GET.get('usage', 'balanced')

    try:
        max_price_float = float(max_price)
    except ValueError:
        max_price_float = 1000.0

    existing_rec = AIPriceRecommendation.objects.filter(
        max_price=max_price_float,
        usage_goal=usage
    ).first()

    if existing_rec:
        if existing_rec.is_valid():
            return render(request, 'result_price_search.html', {'results': [existing_rec], 'max_price': max_price, 'usage': usage})
        else:
            existing_rec.delete()

    ai_data = get_internet_recommendation(max_price_float, usage)
    
    if ai_data:
        new_rec, created = AIPriceRecommendation.objects.update_or_create(
            max_price=max_price_float,
            usage_goal=usage,
            defaults={
                'brand_name': ai_data.get('brand', ''),
                'model_name': ai_data.get('model', ''),
                'antutu_score': ai_data.get('antutu', 0),
                'description': ai_data.get('reason', ''),
                'image_url': ai_data.get('image_url', '')
            }
        )
        results = [new_rec]
    else:
        results = []

    return render(request, 'result_price_search.html', {
        'results': results,
        'max_price': max_price,
        'usage': usage,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home_page')
    else:
        form = AuthenticationForm()
    
    return render(request, 'account/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi tizimga kiring.")
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'account/register.html', {'form': form})

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'account/profile.html')

def logout_view(request):
    logout(request)
    return redirect('home_page')