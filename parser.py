import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတများ ရှင်းလင်းခြင်း (ဒဲ့ အတွက် - ကို မဖျက်ပါ)
    text = text.replace('=', ' ').replace('။', ' ').replace(',', ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    
    grand_total = 0
    pending_units = 0 
    found_any = False

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း']): continue
        
        # 1. Amount ရှာဖွေခြင်း (စာကြောင်းအဆုံးက ဂဏန်း သို့မဟုတ် R/R နောက်က ဂဏန်း)
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])

        # 2. KEYWORDS အရင်ရှာပါ (နင်ပေးထားတဲ့ Order အတိုင်း)
        
        # (A) ၅၀ ကွက်တန် - စုံဘရိတ်/မဘရိတ်
        if any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်', 'စုံbk']):
            line_unit = 50

        # (B) ၂၅ ကွက်တန် - စစ/မမ/စမ/မစ/စုံစုံ/စုံမ
        elif any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_unit = 25 * (2 if is_r else 1)

        # (C) ၂၀ ကွက်တန် - ညီကို/ပတ်ပူး/ပူးပို/ထိပ်ပိတ်/ထိပ်နောက်
        elif any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20

        # (D) ၁၉ ကွက်တန် - ပတ်သီး/အပါ/ပါ/ch/p
        elif any(x in prefix for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']) and 'ပတ်ပူး' not in prefix:
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = (n if n > 0 else 1) * 19

        # (E) ၁၀ ကွက်တန် - ပါဝါ/နက္ခတ်/ဘရိတ်/ထိပ်စီး/အပူး/ဆယ်ပြည့်
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်စီး', 'ထိပ်', 'ထ', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = (n if n > 0 else 1) * 10

        # (F) ၅ ကွက်တန် - စုံပူး/မပူး
        elif any(x in prefix for x in ['စုံပူး', 'မပူး', 'စပူး']):
            line_unit = 5

        # (G) အပူးပါခွေ (N x N)
        elif any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'ပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခပ']):
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = n * n

        # (H) ခွေ (N x N-1)
        elif any(x in prefix for x in ['ခွေ', 'အခွေ', 'ခ']) and 'ခွေပူး' not in prefix:
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = n * (n - 1)

        # (I) ကပ်/ကို (a x b)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            groups = re.findall(r'(\d+)', prefix)
            if len(groups) >= 2:
                line_unit = len(groups[0]) * len(groups[1])
                if is_r: line_unit *= 2

        # (J) Keyword မပါလျှင် (ဒဲ့ - သုံးခြင်း သို့မဟုတ် Space ခြားခြင်း)
        else:
            # Prefix ထဲမှာ ဂဏန်း ၂ လုံးတွဲ ဘယ်နှစ်ခုပါလဲ စစ်သည်
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            elif re.search(r'\d', prefix):
                # ဂဏန်း ၁ လုံးတည်း (ဥပမာ 9 - 500)
                line_unit = len(re.findall(r'\d', prefix)) * (2 if is_r else 1)

        # 3. အပိုင်းလိုက် ပေါင်းတွက်ခြင်း
        if amt > 0:
            grand_total += (pending_units + line_unit) * amt
            pending_units = 0
            found_any = True
        else:
            pending_units += line_unit

    return grand_total if found_any else 0
