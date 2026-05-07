import re

def get_market_rate(text):
    t = text.lower()
    # Market keywords and rates
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို']): return 0.07, "7%"
    if any(x in t for x in ['london', 'လန်လန်', 'လန်ဒန်', 'ld']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    
    # Market နာမည်ရှာမတွေ့ရင် 7% လို့ပဲ သတ်မှတ်ပြီး Admin ခေါ်ဖို့ Return ပြန်မယ်
    return 0.07, None 

def calculate_bets(text):
    lines = text.split('\n')
    lines.reverse() # အောက်က amount ကို အပေါ်ကယူသုံးဖို့
    
    total_sum = 0
    current_amt = 0
    valid_found = False

    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ['2d', 'total', 't=', 'cashback']): continue

        # Amount ရှာခြင်း (Line အဆုံးက ဂဏန်း)
        amt_match = re.search(r'(\d+)$', line)
        if amt_match:
            current_amt = int(amt_match.group(1))
        
        if current_amt == 0: continue

        # --- တွက်ချက်မှု Logic များ ---
        # (အပေါ်က parser logic အတိုင်း အပြည့်အစုံ ပြန်ထည့်ပါ)
        # ၁။ ပတ်သီး/အပါ
        # ၂။ အကပ်/ကို
        # ၃။ အခွေ/ခွေပူး
        # ၄။ ဒဲ့ နှင့် R (ဈေးကွဲ 600R400)
        
        # ဥပမာ ဒဲ့/R အတွက်:
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_val = re.search(r'r(\d+)', line)
            d_val = re.search(r'(\d+)r', line)
            d_amt = int(d_val.group(1)) if d_val else current_amt
            total_sum += len(numbers) * d_amt
            if r_val: total_sum += len(numbers) * int(r_val.group(1))
            elif 'r' in line: total_sum += len(numbers) * d_amt
            valid_found = True

    return total_sum
