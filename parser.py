import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'me', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို']): return 0.07, "7%"
    if any(x in t for x in ['london', 'လန်လန်', 'လန်ဒန်', 'ld']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    return 0.07, None 

def calculate_bets(text):
    # စာလုံးပေါင်း အမှားအယွင်းခံနိုင်အောင် သန့်စင်ခြင်း
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total_sum = 0
    valid_found = False
    processed_data = []

    # 1. Amount ရှာပြီး တွဲခြင်း
    for line in lines:
        l = line.lower()
        if any(x in l for x in ['total', 'cash', 'ကံကောင်း', '2d', 'du', 'me', 't=']): continue
        amt_match = re.search(r'(\d+)$', l)
        amt = int(amt_match.group(1)) if amt_match else 0
        processed_data.append({'txt': l, 'amt': amt})

    # အောက်က amount ကို အပေါ်က ယူသုံးတဲ့ Logic
    for i in range(len(processed_data)):
        if processed_data[i]['amt'] == 0:
            for j in range(i + 1, len(processed_data)):
                if processed_data[j]['amt'] > 0:
                    processed_data[i]['amt'] = processed_data[j]['amt']
                    break

    # 2. တကယ်တွက်ချက်တဲ့အပိုင်း
    for item in processed_data:
        line = item['txt']
        amt = item['amt']
        if amt == 0: continue

        # --- ခွေ / ခွေပူး (၄ လုံးထက်ပိုတဲ့ ဂဏန်းတွေကို အရင်ရှာမယ်) ---
        if any(x in line for x in ['ခွေ', 'ခ']):
            num_match = re.search(r'(\d{3,
