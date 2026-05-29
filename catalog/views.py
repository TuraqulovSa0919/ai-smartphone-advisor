import re
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm  
from django.contrib import messages 
from .models import Smartphone, Brand, AIPriceRecommendation, ContactMessage
from .services import get_phone_ai_analysis, get_internet_recommendation


PRICE_BUCKETS = [
    100, 150, 200, 250, 300, 350, 400, 450, 500,
    550, 600, 650, 700, 750, 800, 850, 900, 950,
    1000, 1100, 1200, 1300, 1400, 1500, 1600, 
    1700, 1800, 1900, 2000, 2200
]

MIN_PRICE = 100
MAX_PRICE = 2200

def get_price_bucket(price):
    """
    Narxni eng yaqin chelakka solish.
    100 dan past → rad etiladi (None qaytaradi)
    2200 dan yuqori → 2200 ga cheklanadi
    """
    if price < MIN_PRICE:
        return None  # Rad etish
    if price > MAX_PRICE:
        return MAX_PRICE
    
    closest = min(PRICE_BUCKETS, key=lambda b: abs(b - price))
    return closest


def home(request):
    """Bosh sahifa"""
    return render(request, 'home.html')


@login_required(login_url='login')
def model_search(request):
    return render(request, 'model_search.html')


@login_required(login_url='login')
def price_search(request):
    return render(request, 'price_search.html', {
        'min_price': MIN_PRICE,
        'max_price': MAX_PRICE,
    })


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
    raw_price = request.GET.get('max_price', '').strip()
    usage = request.GET.get('usage', '').strip()
    error = None

    if not raw_price or not usage:
        error = "Iltimos, narx va maqsadni kiriting."
        return render(request, 'price_search.html', {
            'error': error,
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    try:
        price_float = float(raw_price)
    except ValueError:
        error = "Narx faqat son bo'lishi kerak."
        return render(request, 'price_search.html', {
            'error': error,
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    if price_float < MIN_PRICE:
        error = f"${price_float:.0f} — bu narxda sifatli smartfon topilmaydi. Minimal narx: ${MIN_PRICE}."
        return render(request, 'price_search.html', {
            'error': error,
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    if price_float > MAX_PRICE:
        error = f"${price_float:.0f} — bu narx chegaradan oshib ketdi. Maksimal: ${MAX_PRICE}."
        return render(request, 'price_search.html', {
            'error': error,
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    if usage not in ['gaming', 'camera', 'balanced']:
        error = "Noto'g'ri maqsad tanlandi."
        return render(request, 'price_search.html', {
            'error': error,
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    # ✅ Validatsiya tugadi, endi asosiy logika
    bucketed_price = get_price_bucket(price_float)

    existing_recs = AIPriceRecommendation.objects.filter(
        max_price=bucketed_price,
        usage_goal=usage
    )

    if existing_recs.count() >= 3 and all(r.is_valid() for r in existing_recs):
        return render(request, 'result_price_search.html', {
            'results': list(existing_recs[:3]),
            'user_price': price_float,
            'bucketed_price': bucketed_price,
            'usage': usage,
        })

    existing_recs.delete()

    from django.core.cache import cache
    cache_key = f"ai_request_{bucketed_price}_{usage}"

    if cache.get(cache_key):
        return render(request, 'price_search.html', {
            'error': "Hozir boshqa so'rov bajarilmoqda, biroz kuting.",
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })

    cache.set(cache_key, True, timeout=60)

    try:
        ai_data_list = get_internet_recommendation(bucketed_price, usage)
    except Exception as e:
        return render(request, 'price_search.html', {
            'error': "AI xizmatida xatolik yuz berdi. Qayta urinib ko'ring.",
            'min_price': MIN_PRICE,
            'max_price_limit': MAX_PRICE,
        })
    finally:
        cache.delete(cache_key)

    results = []
    for ai_data in ai_data_list:
        rec = AIPriceRecommendation.objects.create(
            max_price=bucketed_price,
            usage_goal=usage,
            brand_name=ai_data.get('brand', ''),
            model_name=ai_data.get('model', ''),
            cpu=ai_data.get('cpu', ''),
            gpu=ai_data.get('gpu', ''),
            ram=ai_data.get('ram', ''),
            antutu_score=ai_data.get('antutu', 0) or 0,
            global_price=ai_data.get('price', None),
            description=ai_data.get('reason', ''),
            image_url=ai_data.get('image_url', '') or '',
        )
        results.append(rec)

    return render(request, 'result_price_search.html', {
        'results': results,
        'user_price': price_float,
        'bucketed_price': bucketed_price,
        'usage': usage,
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
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
            form.save()
            messages.success(request, "Muvaffaqiyatli ro'yxatdan o'tdingiz!")
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




def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            first_name = request.POST.get('first_name', ''),
            last_name  = request.POST.get('last_name', ''),
            email      = request.POST.get('email', ''),
            subject    = request.POST.get('subject', ''),
            message    = request.POST.get('message', ''),
        )
        messages.success(request, "Xabar yuborildi!")
        return redirect('contact')
    return render(request, 'account/contact.html')