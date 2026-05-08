import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတများကို Space နှင့် မလဲသေးဘဲ သိမ်းထားမည်
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False
    pending_units = 0 

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # Amount ရှာဖွေခြင်း (R ပါသောဂဏန်း သို့မဟုတ် ၃ လုံးနှင့်အထက်ဂဏန်း)
        amt_match = re.search(r'(?:r)?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        
        # Amount ကိုဖယ်ပြီး ကျန်တဲ့အပိုင်း (Prefix) ကိုယူမည်
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = 'r' in line or 'အာ' in line or 'ာ' in line

        # 1. Keyword စစ်ဆေးခြင်း
        if any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * n
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * (n - 1)
        elif any(x in prefix for x in ['ပတ်', 'ပါ', 'အပါ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * 19
        elif any(x in prefix for x in ['bk', 'ဘရိတ်', 'ပါဝါ', 'ညီကို']):
            u = 20 if 'ညီကို' in prefix else 10
            # 456bk500 ဆိုလျှင် 456 ကို multiplier ယူသည်
            m = len("".join(re.findall(r'\d+', prefix))) if re.findall(r'\d+', prefix) else 1
            line_unit = u * m
        else:
            # 2. Keyword မရှိလျှင် ဒဲ့/R (၂ လုံးတွဲများ)
            # 41-46-96 သို့မဟုတ် 45 - 500 ပုံစံများကို စစ်သည်
            two_digits = re.findall(r'\d{2}', prefix)
            line_unit = len(two_digits) * (2 if is_r else 1)

        # တွက်ချက်ခြင်း
        if amt > 0:
            total += (pending_units + line_unit) * amt
            pending_units = 0
            found = True
        else:
            pending_units += line_unit

    return total if found else 0
