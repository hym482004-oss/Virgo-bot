import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # နင်ပြောတဲ့ သင်္ကေတအားလုံးကို Space အဖြစ် ပြောင်းလဲပစ်သည်
    symbols = ['*', '/', "'", '"', '.', '-', '_', '=', '။', '+', '၊']
    for s in symbols:
        text = text.replace(s, ' ')
    
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for i, line in enumerate(lines):
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        amt = int(all_nums[-1])
        
        # အပေါ်စာကြောင်းပါ Context အဖြစ် ယူရန်
        context_text = lines[i-1] + " " + line if i > 0 else line
        line_count = 0
        is_matched = False

        # --- KEYWORDS အုပ်စုများ အကုန်အစုံ ---

        # ၁။ ခွေပူး / အခွေပူး / ပူးပို / အပူးပါခွေ (Formula: n x n)
        if any(x in line for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ', 'အပူးအပြီးပါ']):
            match = re.search(r'(\d+)\s*(?:ခွေပူး|အခွေပူး|ပူးပို|အပူးပါ|အပူးအပြီးပါ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * n
            is_matched = True

        # ၂။ ခွေ / ခ / အခွေ (Formula: n x n-1)
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            match = re.search(r'(\d+)\s*(?:ခွေ|ခ|အခွေ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * (n - 1)
            is_matched = True

        # ၃။ ကပ် / ကို / အကပ် (Formula: a x b)
        elif any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            groups = re.findall(r'(\d+)\s*(?:ကပ်|ကို|အကပ်)\s*(\d+)', context_text)
            if groups:
                line_count = len(groups[0][0]) * len(groups[0][1])
                if any(x in line for x in ['r', 'အာ', 'ာ']): line_count *= 2
                is_matched = True

        # ၄။ ပတ်သီး / အပါ / ပါ (Formula: n x 19)
        elif any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']) and not any(x in line for x in ['ပတ်ပူး']):
            match = re.search(r'(\d+)\s*(?:ပတ်|ပါ|အပါ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * 19
            is_matched = True

        # ၅။ အခြား ပုံသေသတ်မှတ်ချက်များ (၁၀၊ ၂၀၊ ၂၅၊ ၅၊ ၅၀ ကွက်တန်များ)
        if not is_matched:
            unit = 0
            # ၂၀ ကွက်တန်
            if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
                unit += 20
            # ၁၀ ကွက်တန်
            if any(x in line for x in ['ပါဝါ', 'pw', 'power', 'ပဝ', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ထ', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူး', 'ပူး', 'ဆယ်ပြည့်']):
                unit += 10
            # ၅၀ ကွက်တန်
            if any(x in line for x in ['စုံဘရိတ်', 'မဘရိတ်', 'စဘရိတ်']):
                unit += 50
            # ၂၅ ကွက်တန်
            if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
                unit += 25
            # ၅ ကွက်တန်
            if any(x in line for x in ['စုံပူး', 'မပူး']):
                unit += 5
            
            if unit > 0:
                # Keyword ရှေ့မှာ ဂဏန်းတွဲပါသလား စစ်သည်
                match = re.search(r'(\d+)\s*(?:ပါဝါ|ညီကို|bk|ပတ်ပူး|ပူး|ဘရိတ်|ထိပ်|ပိတ်|စုံ|မ)', context_text)
                multiplier = len(match.group(1)) if match else 1
                line_count = unit * multiplier
                is_matched = True

        # ၆။ ဘာ Keyword မှမပါရင် ဒဲ့ / R (၂ လုံးတွဲ)
        if not is_matched:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                line_count = len(two_digits) * (2 if is_r else 1)
                is_matched = True

        if is_matched:
            total += line_count * amt
            found = True

    return total if found else 0
