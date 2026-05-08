import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False
    pending_units = 0 

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # --- 1. Amount ရှာဖွေခြင်း (R ပါသော ဂဏန်း သို့မဟုတ် ၃ လုံးနှင့်အထက်) ---
        amt_match = re.search(r'(?:r|R)?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        
        # Amount ကို ဖယ်ပြီး ကျန်သည့် အပိုင်း (Prefix)
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = any(x in line.lower() for x in ['r', 'အာ', 'ာ'])

        # --- 2. Keywords များကို ဦးစားပေး ရှာဖွေတွက်ချက်ခြင်း ---
        
        # (A) ၅၀ ကွက်တန် - စုံဘရိတ်/မဘရိတ်
        if any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_unit = 50
        
        # (B) ၂၅ ကွက်တန် - စစ/မမ/စမ/မစ/စုံစုံ/စုံမ
        elif any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_unit = 25 * (2 if is_r else 1)

        # (C) ၂၀ ကွက်တန် - ညီကို/ပတ်ပူး/ပူးပို/ထန/ထပ/ထိပ်ပိတ်
        elif any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20

        # (D) ၁၉ ကွက်တန် - ပတ်သီး/အပါ/ပါ/ch/p
        elif any(x in prefix for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']) and 'ပတ်ပူး' not in prefix:
            n_match = re.findall(r'\d', prefix)
            line_unit = len(n_match) * 19

        # (E) ၁၀ ကွက်တန် - ပါဝါ/နက္ခတ်/ဘရိတ်/ထိပ်/အပိတ်/အပူး/ဆယ်ပြည့်
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'နက', 'နခ', 'nk', 'ဘရိတ်', 'bk', 'ထိပ်', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            multiplier = len(re.findall(r'\d', prefix)) if re.findall(r'\d', prefix) else 1
            line_unit = multiplier * 10

        # (F) ၅ ကွက်တန် - စုံပူး/မပူး
        elif any(x in prefix for x in ['စုံပူး', 'မပူး', 'စပူး']):
            line_unit = 5

        # (G) ခွေပူး / အပူးပါခွေ (N x N)
        elif any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'ပူး', 'အပူးပါ', 'အပူးအပြီးပါ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * n

        # (H) ခွေ (N x N-1)
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * (n - 1)

        # (I) ကပ် / ကို (a x b)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            groups = re.findall(r'(\d+)', prefix)
            if len(groups) >= 2:
                line_unit = len(groups[0]) * len(groups[1])
                if is_r: line_unit *= 2

        # (J) ဒဲ့ သို့မဟုတ် Symbol (- = ဒဲ့)
        else:
            # ဂဏန်း ၂ လုံးတွဲများကို ရှာသည်
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            elif re.match(r'^\d$', prefix): # ဂဏန်းတစ်လုံးတည်း (ဥပမာ 9 - 500)
                line_unit = 1

        # --- 3. တွက်ချက်ခြင်း ---
        if amt > 0:
            total += (pending_units + line_unit) * amt
            pending_units = 0
            found = True
        else:
            # Amount မပါသေးသော စာကြောင်းများကို မှတ်ထားသည်
            pending_units += line_unit

    return total if found else 0
