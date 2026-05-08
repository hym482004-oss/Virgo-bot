import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတအားလုံးကို ရှင်းလင်းပြီး Space အဖြစ် ပြောင်းသည် (ဒဲ့ အတွက် - ကို ခဏချန်မည်)
    symbols = ['*', '/', "'", '"', '.', '_', '=', '။', '+', '၊']
    for s in symbols:
        text = text.replace(s, ' ')
    
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False
    pending_units = 0

    for i, line in enumerate(lines):
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # Amount ရှာဖွေခြင်း (စာကြောင်းအဆုံးက ၃ လုံးနှင့်အထက် သို့မဟုတ် R ပါသောဂဏန်း)
        amt_match = re.search(r'(?:r|R)?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = any(x in line.lower() for x in ['r', 'အာ', 'ာ'])

        # --- KEYWORD LOGIC ---
        
        # (1) ၂၀ ကွက်တန်
        if any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20
        
        # (2) ၁၀ ကွက်တန်
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'နက', 'နခ', 'nk', 'ဘရိတ်', 'bk', 'ထိပ်စီး', 'ထိပ်', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            nums = "".join(re.findall(r'\d', prefix))
            multiplier = len(nums) if nums else 1
            line_unit = multiplier * 10

        # (3) ပတ်သီး (၁၉ ကွက်)
        elif any(x in prefix for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = "".join(re.findall(r'\d', prefix))
            line_unit = len(nums) * 19 if nums else 19

        # (4) ခွေပူး (n x n)
        elif any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ']):
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = n * n

        # (5) ခွေ (n x n-1)
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            n = len("".join(re.findall(r'\d', prefix)))
            line_unit = n * (n - 1)

        # (6) ကပ် / ကို
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            groups = re.findall(r'(\d+)', prefix)
            if len(groups) >= 2:
                line_unit = len(groups[0]) * len(groups[1])
                if is_r: line_unit *= 2

        # (7) ၅၀၊ ၂၅၊ ၅ ကွက်တန်များ
        elif any(x in prefix for x in ['စုံဘရိတ်', 'မဘရိတ်', 'စဘရိတ်', 'စုံbk', 'မbk']):
            line_unit = 50
        elif any(x in prefix for x in ['စစ', 'မမ', 'စုံစုံ', 'စုံမ', 'စမ', 'မစ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_unit = 25 * (2 if is_r else 1)
        elif any(x in prefix for x in ['စုံပူး', 'မပူး', 'စပူး']):
            line_unit = 5

        # (8) ဒဲ့ သို့မဟုတ် Symbol ( - )
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            elif re.search(r'\d', prefix): # တစ်လုံးချင်းစီ ဒဲ့တွက်ရန်
                line_unit = len(re.findall(r'\d', prefix)) * (2 if is_r else 1)

        # --- FINAL TOTALING ---
        if amt > 0:
            total += (pending_units + line_unit) * amt
            pending_units = 0
            found = True
        else:
            pending_units += line_unit

    return total if found else 0
