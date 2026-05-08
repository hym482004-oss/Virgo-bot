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
        
        # စာသားထဲက Amount (နောက်ဆုံးဂဏန်း) ကို အရင်ရှာသည်
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        amt = int(all_nums[-1])
        
        # Amount မဟုတ်တဲ့ ကျန်တဲ့ ဂဏန်းတွေကို စုစည်းသည် (ဥပမာ - 156)
        other_nums_str = "".join(all_nums[:-1])
        
        line_valid = False
        unit_count = 0

        # --- STEP 1: Keyword အလိုက် အကွက်အရေအတွက် သတ်မှတ်ခြင်း ---
        # ၁၀ ကွက်တန်များ
        if any(x in line for x in ['ပါဝါ', 'pw', 'power', 'ပဝ', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ထ', 'ပိတ်', 'အနောက်', 'အပူး', 'ပူး']):
            unit_count += 10
            line_valid = True
        # ၂၀ ကွက်တန်များ
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်']):
            unit_count += 20
            line_valid = True
        # ၅၀ ကွက်တန်များ
        if any(x in line for x in ['စုံဘရိတ်', 'မဘရိတ်', 'စဘရိတ်']):
            unit_count += 50
            line_valid = True
        # ၁၉ ကွက်တန် (ပတ်သီး)
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']) and not any(x in line for x in ['ပတ်ပူး', 'ပူးပို']):
            unit_count += 19
            line_valid = True

        # --- STEP 2: စုစုပေါင်း တွက်ချက်ခြင်း ---
        if line_valid:
            # အကယ်၍ 156bk လို့ရေးရင် 1, 5, 6 တစ်လုံးချင်းစီအတွက် unit_count နဲ့ မြှောက်မည်
            group_multiplier = len(other_nums_str) if other_nums_str else 1
            total += (group_multiplier * unit_count) * amt
            found = True
        else:
            # ခွေ / ခွေပူး Logic (သီးသန့် Formula သုံးသည်)
            if any(x in line for x in ['ခွေပူး', 'အခွေပူး']):
                n = len(other_nums_str)
                total += (n * n) * amt
                found = True
            elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
                n = len(other_nums_str)
                total += (n * (n - 1)) * amt
                found = True
            else:
                # ဒဲ့ / R (၂ လုံးတွဲ)
                two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
                if two_digits:
                    is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                    total += len(two_digits) * amt * (2 if is_r else 1)
                    found = True

    return total if found else 0
