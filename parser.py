import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတများကို ရှင်းလင်းခြင်း
    for s in ['*', '-', "'", '/', '.', '=', '။', '+']:
        text = text.replace(s, ' ')
    
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        
        # Amount က အမြဲတမ်း နောက်ဆုံးဂဏန်းဖြစ်ရမည်
        amt = int(all_nums[-1])
        line_valid = False
        line_count = 0

        # --- STEP 1: KEYWORD ရှာဖွေခြင်း နှင့် ပုံသေနည်းဖြင့် တွက်ချက်ခြင်း ---

        # (6) ခွေပူး / အပူးပါခွေ (Formula: n x n)
        if any(x in line for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ', 'အပူးအပြီးပါ']):
            n_match = re.search(r'(\d{3,10})', line)
            if n_match:
                n = len(n_match.group(1))
                line_count = n * n
                line_valid = True

        # (5) ခွေ (Formula: n x n-1)
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            n_match = re.search(r'(\d{3,10})', line)
            if n_match:
                n = len(n_match.group(1))
                line_count = n * (n - 1)
                line_valid = True

        # (9) ကပ် / ကို (Formula: a_len x b_len)
        elif any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            if len(all_nums) >= 3: # ဂဏန်းအုပ်စု ၂ ခု + Amount
                line_count = len(all_nums[0]) * len(all_nums[1])
                # R ပါရင် ၂ ဆမြှောက်ရန်
                if any(x in line for x in ['r', 'အာ', 'ာ']):
                    line_count *= 2
                line_valid = True

        # (4) ပတ်သီး (Formula: n x 19)
        elif any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']) and not any(x in line for x in ['ပတ်ပူး', 'ပူးပို']):
            # 'ပတ်' ရှေ့က ဂဏန်းအရေအတွက်ကို ယူသည်
            n_str = line.split('ပတ်')[0].strip()
            n_digits = re.findall(r'\d', n_str)
            multiplier = len(n_digits) if n_digits else 1
            line_count = multiplier * 19
            line_valid = True

        # (1, 11, 10, 8, 7) အခြား ပုံသေ အကွက်အရေအတွက်များ
        else:
            # ၂၀ ကွက်တန်များ
            if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
                line_count = 20
                line_valid = True
            # ၁၀ ကွက်တန်များ
            elif any(x in line for x in ['ပါဝါ', 'pw', 'power', 'ပဝ', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ထ', 'ပိတ်', 'အနောက်', 'အပူး', 'ပူး', 'ဆယ်ပြည့်']):
                line_count = 10
                line_valid = True
            # ၅၀ ကွက်တန်များ
            elif any(x in line for x in ['စုံဘရိတ်', 'မဘရိတ်', 'စဘရိတ်']):
                line_count = 50
                line_valid = True
            # ၂၅ ကွက်တန်များ
            elif any(x in line for x in ['စစ', 'မမ', 'စုံစုံ']):
                line_count = 25
                if any(x in line for x in ['r', 'အာ', 'ာ']): line_count *= 2
                line_valid = True
            # ၅ ကွက်တန်များ
            elif any(x in line for x in ['စုံပူး', 'မပူး']):
                line_count = 5
                line_valid = True

        # --- STEP 2: KEYWORD မပါလျှင် ဒဲ့ / R စစ်ဆေးခြင်း (၂ လုံးတွဲ) ---
        if not line_valid:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                total += len(two_digits) * amt * (2 if is_r else 1)
                line_valid = True
        else:
            # Keyword တွေ့လျှင် တွက်ထားသော အကွက်အရေအတွက်ကို Amount နှင့် မြှောက်သည်
            total += line_count * amt

        if line_valid: found = True

    return total if found else 0
