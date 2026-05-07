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

    for line in lines:
        if any(x in line for x in ['total', 'cash', 'တွက်', '2d']): continue
        
        amt_match = re.findall(r'\d+', line)
        if not amt_match: continue
        amt = int(amt_match[-1])

        line_total_count = 0
        
        # --- ခွေပူး (n * n) ---
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အခွေပူး']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                line_total_count += (n * n)
        
        # --- ခွေ (n * (n-1)) ---
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                line_total_count += (n * (n - 1))

        # --- ၁၀ ကွက်တန် Keyword များ ---
        ten_keys = {'power':['ပါဝါ','pw','ပဝ'], 'nk':['နက္ခတ်','nk','နက'], 
                    'double':['အပူး','ပူး'], 'top':['ထိပ်','ထ','t'], 
                    'bk':['ဘရိတ်','bk'], 'ten':['ဆယ်']}
        
        for key, patterns in ten_keys.items():
            if any(p in line for p in patterns):
                if key == 'bk':
                    # 135bk လိုမျိုးအတွက်
                    n_part = line.split('bk')[0]
                    n_count = len(re.findall(r'\d', n_part))
                    line_total_count += (n_count if n_count > 0 else 1) * 10
                else:
                    line_total_count += 10

        # --- ၂၀ ကွက်တန် (ညီကို) ---
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']):
            line_total_count += 20

        # --- ၅၀ ကွက်တန် (စုံဘရိတ်) ---
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk']):
            line_total_count += 50

        # --- ၂၅ ကွက်တန် (စစ/မမ) ---
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ']):
            line_total_count += 25 * (2 if 'r' in line or 'အာ' in line else 1)

        # --- ၂ လုံးတွဲ ဒဲ့ / R ---
        # Keyword တစ်ခုမှ မပါမှ ဒဲ့ဂဏန်း ရှာမယ်
        if line_total_count == 0:
            nums = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if nums:
                line_total_count += len(nums) * (2 if 'r' in line or 'အာ' in line else 1)

        if line_total_count > 0:
            total += line_total_count * amt
            found = True

    return total if found else 0
