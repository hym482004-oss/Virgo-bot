import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    for s in ['*', '-', "'", '/', '.', '=', '။']:
        text = text.replace(s, ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        
        # Amount ကို နောက်ဆုံးဂဏန်းအဖြစ် သတ်မှတ်သည်
        amt = int(all_nums[-1])
        line_valid = False
        line_count = 0

        # --- Keyword တစ်ခုချင်းစီအတွက် အကွက်အရေအတွက် သတ်မှတ်ခြင်း ---
        # (1) ၁၀ ကွက်တန်များ
        ten_keys = ['ပါဝါ', 'pw', 'power', 'ပဝ', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ထ', 'top', 't', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်']
        for k in ten_keys:
            if k in line:
                line_count += 10
                line_valid = True

        # (11) ၂၀ ကွက်တန်များ
        twenty_keys = ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']
        if any(x in line for x in twenty_keys):
            line_count += 20
            line_valid = True

        # (10) ၅၀ ကွက်တန်
        if any(x in line for x in ['စုံဘရိတ်', 'မဘရိတ်']):
            line_count += 50
            line_valid = True

        # (4) ၁၉ ကွက်တန် (ပတ်သီး)
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']) and not any(x in line for x in ['ပတ်ပူး', 'ပူးပို']):
            n_match = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            # ဂဏန်းဘယ်နှလုံးကို ပတ်မလဲ စစ်သည်
            multiplier = len(n_match) if n_match else 1
            line_count += multiplier * 19
            line_valid = True

        # (2, 3) ဒဲ့ / R (၂ လုံးတွဲ) - အပေါ်က Keyword တွေ မပါမှ စစ်မည်
        if not line_valid:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                total += len(two_digits) * amt * (2 if is_r else 1)
                line_valid = True
        else:
            # Keyword ပါရင် တွက်ထားတဲ့ line_count နဲ့ မြှောက်သည်
            total += line_count * amt

        if line_valid: found = True

    return total if found else 0
