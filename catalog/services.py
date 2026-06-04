import json
import re
from google import genai
from google.genai import types
from config import Config
from django.utils import timezone
from datetime import timedelta

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_phone_ai_analysis(phone_name, existing_brands):
    brands_str = ", ".join(existing_brands)
    
    prompt = f"""
    Bugungi sana: 15-Aprel, 2026-yil.
    Smartfon: "{phone_name}". 
    Bazadagi brendlar: [{brands_str}]. 
    
    QAT'IY QOIDALAR: 
    1. Foydalanuvchi AYNAN "{phone_name}" ni so'rayapti. Bu model internetda aniq bor, shuning uchun Google Search orqali diqqat bilan qidir!
    2. Agar qidiruv natijalarida "{phone_name}" va "{phone_name} Pro/Ultra" aralashib kelsa, IKKALASINI ADASHTIRMA! Faqatgina oddiy "{phone_name}" (Base model) xususiyatlarini ajratib ol.
    3. Menga Pro, Max yoki Ultra xususiyatlarini yuborma. FAQAT o'zining (oddiy versiyasining) parametrlarini yoz.
    4. Antutu bali aniqligiga qattiq ahamiyat ber.
    5. (UZUM, ASSAXIY, RADIUS, OLCHA kabi ishonchli manbalardan narx topishga harakat qil) - Narxni ham aniq yoz, lekin agar narx topilmasa, "N/A" deb yoz. 
    6. Rasm linkini olishda asosgan GSM-ARENA saytidan foydalan. Agar rasm linkini  topishda qiynalgan va yoki ishonchsiz link deb shubhalansang, "N/A" deb yoz. 
    
    Javobni FAQAT JSON formatida ber.
    JSON STRUKTURASI:
    {{
        "brand_name": "Brend nomi",
        "model_name": "Aniq model nomi (Pro so'zini qo'shma!)",
        "cpu": "Protsessor nomi",
        "gpu": "Grafik chip nomi",
        "ram": "8/12/16 GB",
        "storage": "256/512/1TB GB",
        "camera": "Asosiy kameralar",
        "old_camera": "Old kamera",
        "battery": 5000,
        "antutu": 2500000,
        "body": "Korpus materiali",
        "extras": "Qo'shimcha imkoniyatlar",
        "user_feedback": {{"yaxshi": 85, "ortacha": 10, "yomon": 5}},
        "global_price": "$300",
        "uzb_price": "4,500,000 so'm",
        "full_analysis": "AI Ekspert maslahati: Yakuniy xulosa.",
        "image_url": "Rasmiy .jpg yoki .png rasm linki"
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                temperature=0.0
            )
        )
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"AI Xatosi: {e}")
        return None
    

def get_budget_recommendation(max_price, usage, all_brands):
    usage_map = {
        'gaming': 'o\'yin o\'ynash va yuqori unumdorlik (high performance, Antutu score)',
        'camera': 'sifatli rasm va video olish (best camera setup)',
        'balanced': 'har tomonlama balanslashgan, kundalik foydalanish va batareya chidamliligi'
    }
    
    prompt = f"""
    Menga maksimal {max_price}$ byudjetda {usage_map.get(usage, 'umumiy')} maqsadlar uchun eng yaxshi smartfon modelini topib ber.
    Javobni faqat JSON formatida qaytar:
    {{
        "brand_name": "brend nomi",
        "model_name": "model nomi",
        "why_this": "nima uchun aynan shu model tanlanganligi haqida qisqa izoh (o'zbek tilida)"
    }}
    """
    
    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0)
        )
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"AI Tavsiya Xatosi: {e}")
        return None
    
def get_internet_recommendation(price, usage):
    usage_map = {
        'gaming': "o'yin o'ynash (eng yuqori unumdorlik, eng katta AnTuTu bali)",
        'camera': "sifatli rasm va video olish (eng yaxshi kamera, optik stabilizatsiya)",
        'balanced': "har tomonlama muvozanatli (batareya va barqaror ishlash)"
    }
    
    min_price = max(0, price - 30)
    max_price = price
    
    prompt = f"""
    Bugungi sana: 2026-yil.
    Vazifa: Google Search orqali ${min_price} - ${max_price} oralig'ida, {usage_map.get(usage, 'umumiy')} maqsadlar uchun ENG YAXSHI 3 ta smartfonni top.
    
    QAT'IY SHARTLAR:
    1. NARX CHEKLOVI: Narx hech qachon ${max_price} dan oshmasligi shart!
    2. 3 TA TURLI MODEL: Har xil brendlardan bo'lishi afzal (masalan: Samsung, Xiaomi, OnePlus) yoki boshqa.
    3. "image_url": GSMArena yoki rasmiy saytdan to'g'ridan to'g'ri .jpg/.png link. Ishonchsiz bo'lsa N/A yoz.
    4. TARKIBI TO'LIQ: "cpu", "gpu", "ram", "antutu" maydonlari bo'sh qolmasin.
    5. BREND VA MODEL: "brand" faqat brend ("Xiaomi"), "model" qolgan qismi ("15").
    6. TARTIBLASH: Eng kuchligidan boshlab tartiblangan bo'lsin.
    7. TIL: BARCHA matnlar, jumladan "reason" maydoni ham O'ZBEK tilida bo'lsin!
    8. HAQIQIY NARX: "price" maydoniga telefonning HAQIQIY bozor narxini yoz, ${max_price} emas!
    
    Javobni FAQAT JSON array formatida qaytar (boshqa matn yozma):
    [
        {{
            "brand": "Brend nomi",
            "model": "Model nomi",
            "cpu": "Protsessor nomi",
            "gpu": "Grafika nomi",
            "ram": "8/12/16 GB",
            "antutu": 2000000,
            "price": 470,
            "reason": "Nima uchun tanlandi? O'ZBEK TILIDA qisqa izoh.",
            "image_url": "Rasmiy .jpg yoki .png rasm linki yoki N/A"
        }},
        {{ ... }},
        {{ ... }}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                temperature=0.0
            )
        )

        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)

        if match:
            data = json.loads(match.group(0))
            return data[:3] if isinstance(data, list) else []

        print("JSON array topilmadi. Raw:", cleaned_text[:500])
        return []

    except Exception as e:
        print(f"AI Narx Tavsiyasi Xatosi: {e}")
        return []