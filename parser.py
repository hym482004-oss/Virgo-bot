import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတများရှင်းလင်းခြင်း
    for s in ['*', '-', "'", '/', '.', '=', '။', '+']:
        text = text.replace(s, ' ')
    
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # Line ထဲမှာပါတဲ့ ဂဏန်းအားလုံးကို အရင်ထုတ်သည်
        nums = re.findall(r'\d+', line)
        if not nums: continue
        amt = int(nums[-1]) # နောက်ဆုံးဂဏန်းကို Amount အဖြစ်သတ်မှတ်
        
        line_count = 0
        is_matched = False

        # 1. ခွေပူး (n * n)
        if any(x in line for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ']):
            match = re.search(r'(\d+)\s*(?:ခွေပူး|အခွေပူး|ပူးပို|အပူးပါ)', line)
            n = len(match.group(1)) if match else 0
            line_count = n * n
            is_matched = True

        # 2. ခွေ (n * n-1)
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            match = re.search(r'(\d+)\s*(?:ခွေ|ခ|အခွေ)', line)
            n = len(match.group(1)) if match else 0
            line_count = n * (n - 1)
            is_matched = True

        # 3. ပတ်သီး (n * 19)
        elif any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']):
            match = re.search(r'(\d+)\s*(?:ပတ်|ပါ|အပါ)', line)
            n = len(match.group(1)) if match else 0
            line_count = n * 19
            is_matched = True

        # 4. ၁၀/၂၀ ကွက်တန် Keywords များ (ညီကို၊ ပါဝါ၊ ဘရိတ်)
        if not is_matched:
            current_unit = 0
            if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): current_unit += 20
            if any(x in line for x in ['ပါဝါ', 'pw', 'power']): current_unit += 10
            if any(x in line for x in ['ဘရိတ်', 'bk']): current_unit += 10
            
            if current_unit > 0:
                # Keyword ရှေ့မှာ ဂဏန်းတွဲပါသလား စစ်သည် (ဥပမာ - 15bk)
                match = re.search(r'(\d+)\s*(?:ညီကို|ပါဝါ|bk|pw|power|ဘရိတ်)', line)
                multiplier = len(match.group(1)) if match else 1
                line_count = current_unit * multiplier
                is_matched = True

        # 5. ဘာ Keyword မှမပါလျှင် ဒဲ့ / R (၂ လုံးတွဲ)
        if not is_matched:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                line_count = len(two_digits) * (2 if is_r else 1)
                is_matched = True

        # စုစုပေါင်းပေါင်းခြင်း
        if is_matched:
            total += line_count * amt
            found = True

    return total if found else 0
