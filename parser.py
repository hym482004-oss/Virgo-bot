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
        
        # Amount (R ပါသော ဂဏန်း သို့မဟုတ် ၃ လုံးနှင့်အထက်) ကို ရှာသည်
        amt_match = re.search(r'(?:r|R)?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        
        # Amount ကို ဖယ်ပြီး ကျန်သည့် အပိုင်း
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        line_unit = 0
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])

        # 1. Keywords အားလုံးကို အုပ်စုအလိုက် ဦးစားပေး စစ်ဆေးခြင်း
        if any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * n
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * (n - 1)
        elif any(x in prefix for x in ['ပတ်', 'ပါ', 'အပါ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * 19
        elif any(x in prefix for x in ['bk', 'ဘရိတ်', 'ပါဝါ', 'ညီကို', 'နက္ခတ်', 'nk', 'ပဝ', 'ထိပ်', 'ပိတ်']):
            u = 20 if 'ညီကို' in prefix else 10
            m = len("".join(re.findall(r'\d+', prefix))) if re.findall(r'\d+', prefix) else 1
            line_unit = u * m
        elif any(x in prefix for x in ['စုံဘရိတ်', 'မဘရိတ်']):
            line_unit = 50
        # 2. Keyword မပါလျှင် Symbol (- = ဒဲ့) သို့မဟုတ် Space ခြားထားသော ၂ လုံးတွဲများ
        else:
            # Prefix ထဲက ၂ လုံးတွဲ ဂဏန်းအားလုံးကို ထုတ်သည်
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)

        # 3. တွက်ချက်ခြင်း (Amount တွေ့လျှင် ပေါင်းမြှောက်မည်)
        if amt > 0:
            total += (pending_units + line_unit) * amt
            pending_units = 0
            found = True
        else:
            # Amount မတွေ့သေးလျှင် Pending လုပ်ထားမည်
            pending_units += line_unit

    return total if found else 0
