import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, None

def calculate_bets(text):
    text = text.lower().replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total = 0
    found = False
    
    # Keyword တွက်နည်း Patterns
    patterns = {
        'bro': ['ညီကို', 'ညီအကို', 'ညီအစ်ကို'], # 20 ကွက်
        'power': ['ပါဝါ', 'pw', 'ပဝ'], # 10 ကွက်
        'nk': ['နက္ခတ်', 'nk', 'နက', 'နခ'], # 10 ကွက်
        'double': ['အပူး', 'ပူး'], # 10 ကွက်
        'top': ['ထိပ်', 'ထ', 'top', 't'], # 10 ကွက်
        'bk': ['ဘရိတ်', 'bk'], # 10 ကွက်
        'full_ten': ['ဆယ်'], # 10 ကွက်
    }

    for line in lines:
        if any(x in line for x in ['total', 'cash', 'တွက်']): continue
        
        amt_match = re.findall(r'\d+', line)
        if not amt_match: continue
        amt = int(amt_match[-1])

        line_valid = False
        
        # တစ်ကြောင်းထဲမှာ Keyword အစုံပါရင် အကုန်ပေါင်းတွက်မယ်
        # ၁၀ ကွက်တန် Keyword များ
        for key in ['power', 'nk', 'double', 'top', 'bk', 'full_ten']:
            if any(x in line for x in patterns[key]):
                if key == 'bk':
                    # 135bk လိုမျိုး ရှေ့ကဂဏန်းအရေအတွက်ကို ယူမယ်
                    nums = re.findall(r'\d', line.split('bk')[0])
                    count = len(nums) if nums else 1
                    total += count * 10 * amt
                else:
                    total += 10 * amt
                line_valid = True

        # ၂၀ ကွက်တန် (ညီကို)
        if any(x in line for x in patterns['bro']):
            total += 20 * amt
            line_valid = True

        # ၅၀ ကွက်တန် (စုံဘရိတ်)
        if any(x in line for x in ['စုံဘရိတ်', 'စဘရိတ်', 'စုံbk']):
            total += 50 * amt
            line_valid = True

        # ၂၅ ကွက်တန် (စစ/မမ)
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ']):
            total += 25 * amt * (2 if 'r' in line or 'အာ' in line else 1)
            line_valid = True

        # ခွေ/ခွေပူး
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အခွေပူး']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * n) * amt
                line_valid = True
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * (n - 1)) * amt
                line_valid = True

        # ၂ လုံးတွဲ (ဒဲ့/R)
        # Keyword တစ်ခုမှ မပါမှ ၂ လုံးတွဲ သီးသန့် ရှာမယ်
        if not any(k in line for k in ['ပတ်', 'ပါ', 'ကို', 'ကပ်', 'ခွေ', 'ဘရိတ်', 'ညီကို', 'ပါဝါ', 'နက္ခတ်', 'အပူး']):
            nums = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if nums:
                total += len(nums) * amt * (2 if 'r' in line or 'အာ' in line else 1)
                line_valid = True
        
        if line_valid: found = True

    return total if found else 0
