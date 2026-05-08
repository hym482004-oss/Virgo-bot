import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတများကို ရှင်းလင်းခြင်း (= ကို Space ပြောင်းသည်)
    text = text.replace('=', ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    
    total = 0
    found = False
    pending_units = 0 # Amount မပါသေးသော အကွက်များကို စုရန်

    for line in lines:
        # လုပ်ငန်းသုံး စာလုံးများပါလျှင် ကျော်မည်
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း']): continue
        
        # ၁။ Amount (ကြေး) ကို အရင်ရှာသည်
        # စာကြောင်းအဆုံးရှိ ၃ လုံးနှင့်အထက်ဂဏန်း သို့မဟုတ် R နောက်က ဂဏန်း
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        
        # Amount ကိုဖယ်ပြီး ကျန်တဲ့အပိုင်း (ဂဏန်းနဲ့ Keyword များ)
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])

        # ၂။ Keywords များကို ဦးစားပေး ရှာဖွေတွက်ချက်ခြင်း
        
        # (A) ၂၀ ကွက်တန် - ထိပ်ပိတ်၊ ညီကို၊ ပတ်ပူး
        if any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20
            
        # (B) ၁၀ ကွက်တန် - bk, ပါဝါ, နက္ခတ်, ထိပ်, ပိတ်
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'နက္ခတ်', 'nk', 'ဘရိတ်', 'bk', 'ထိပ်', 'ပိတ်', 'နောက်', 'အပူး', 'ဆယ်ပြည့်']):
            nums = re.findall(r'\d', prefix)
            multiplier = len(nums) if nums else 1
            line_unit = multiplier * 10
            
        # (C) ခွေပူး / အခွေပူး (n x n)
        elif any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ']):
            nums = "".join(re.findall(r'\d', prefix))
            n = len(nums)
            line_unit = n * n
            
        # (D) ခွေ (n x n-1)
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = "".join(re.findall(r'\d', prefix))
            n = len(nums)
            line_unit = n * (n - 1)
            
        # (E) ပတ်သီး (၁၉ ကွက်)
        elif any(x in prefix for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', prefix)
            line_unit = len(nums) * 19 if nums else 19

        # (F) ၂၅ ကွက်တန် နှင့် ၅၀ ကွက်တန်
        elif any(x in prefix for x in ['စစ', 'မမ', 'စုံစုံ', 'စုံဘရိတ်', 'မဘရိတ်']):
            line_unit = 50 if 'ဘရိတ်' in prefix else 25
            if is_r: line_unit *= 2

        # (G) Keyword လုံးဝမပါလျှင် (ဒဲ့/R)
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            else:
                # 5-0 bk250 ထဲက 5-0 လိုမျိုး
                single_digits = re.findall(r'\d', prefix)
                if single_digits:
                    line_unit = len(single_digits) * (2 if is_r else 1)

        # ၃။ Section အလိုက် ပေါင်းတွက်ခြင်း
        if amt > 0:
            # Amount တွေ့လျှင် လက်ရှိစာကြောင်းရော၊ အပေါ်က စာကြောင်းတွေပါ ပေါင်းမြှောက်မည်
            total += (pending_units + line_unit) * amt
            pending_units = 0 # Amount သုံးပြီးလျှင် Buffer ကို ပြန်ရှင်းမည်
            found = True
        else:
            # Amount မပါသေးလျှင် အကွက်ရေကို မှတ်ထားမည်
            pending_units += line_unit

    return total if found else 0
