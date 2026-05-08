import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    for s in ['*', '-', "'", '/', '.', '=', '။', '+']:
        text = text.replace(s, ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        amt = int(all_nums[-1]) # နောက်ဆုံးဂဏန်းကို Amount ယူသည်
        
        line_valid = False
        line_count = 0

        # (6) ခွေပူး / အပူးပါခွေ (n * n)
        if any(x in line for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ']):
            # Keyword ရှေ့က ဂဏန်းများကို ရှာသည်
            match = re.search(r'(\d+)\s*(?:ခွေပူး|အခွေပူး|ပူးပို|အပူးပါ)', line)
            if match:
                n = len(match.group(1))
                line_count = n * n
                line_valid = True

        # (5) ခွေ (n * n-1)
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            match = re.search(r'(\d+)\s*(?:ခွေ|ခ|အခွေ)', line)
            if match:
                n = len(match.group(1))
                line_count = n * (n - 1)
                line_valid = True

        # (4) ပတ်သီး (n * 19)
        elif any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']) and not any(x in line for x in ['ပတ်ပူး']):
            match = re.search(r'(\d+)\s*(?:ပတ်|ပါ|အပါ)', line)
            if match:
                n = len(match.group(1))
                line_count = n * 19
                line_valid = True

        # (1, 11) အခြား Keyword များ (ညီကို၊ ပါဝါ၊ bk)
        if not line_valid:
            temp_count = 0
            if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): temp_count += 20
            if any(x in line for x in ['ပါဝါ', 'pw', 'power']): temp_count += 10
            if any(x in line for x in ['ဘရိတ်', 'bk']): temp_count += 10
            
            if temp_count > 0:
                # ဂဏန်းအုပ်စု ပါ/မပါ စစ်သည် (ဥပမာ- 156bk)
                match = re.search(r'(\d+)\s*(?:ညီကို|ပါဝါ|bk|pw|power|ဘရိတ်)', line)
                multiplier = len(match.group(1)) if match else 1
                line_count = multiplier * temp_count
                line_valid = True

        # --- နောက်ဆုံးတွက်ချက်မှု ---
        if line_valid:
            total += line_count * amt
            found = True
        else:
            # ဒဲ့ / R (၂ လုံးတွဲ)
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                total += len(two_digits) * amt * (2 if is_r else 1)
                found = True

    return total if found else 0
