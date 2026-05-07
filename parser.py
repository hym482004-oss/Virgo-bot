import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t:
        return 0.10, "10%"
    if any(x in t for x in ['global', 'glo']):
        return 0.03, "3%"
    return 0.07, None

def calculate_bets(text):
    text = text.lower().replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    total = 0
    found = False
    processed_data = []

    # Amount ရှာဖွေခြင်း
    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'du', 'me']): continue
        amt_match = re.findall(r'\d+', line)
        amt = int(amt_match[-1]) if amt_match else 0
        processed_data.append({'txt': line, 'amt': amt})

    for i in range(len(processed_data)):
        if processed_data[i]['amt'] == 0:
            for j in range(i + 1, len(processed_data)):
                if processed_data[j]['amt'] > 0:
                    processed_data[i]['amt'] = processed_data[j]['amt']
                    break

    for item in processed_data:
        line = item['txt']
        amt = item['amt']
        if amt == 0: continue

        # --- ခွေပူး (n * n) ---
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အခွေပူး', 'ပူး']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * n) * amt
                found = True; continue

        # --- ခွေ (n * (n-1)) ---
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * (n - 1)) * amt
                found = True; continue

        # --- ပတ်သီး / အပါ (၁၉ ကွက် သို့မဟုတ် ၂၀ ကွက်) ---
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်', 'ပတ်ပူး']) else 19
            total += (len(nums) if nums else 1) * count * amt
            found = True; continue

        # --- ထိပ် / ဘရိတ် / ပါဝါ / နက္ခတ် / ဆယ်ပြည့် (၁၀ ကွက်တန်များ) ---
        if any(x in line for x in ['ထိပ်', 'ထ', 'top', 't', 'ဘရိတ်', 'bk', 'ပါဝါ', 'pw', 'ပဝ', 'နက္ခတ်', 'nk', 'ဆယ်']):
            nums_part = line.split('bk')[0] if 'bk' in line else line
            nums = re.findall(r'\d', nums_part)
            total += (len(nums) if nums else 1) * 10 * amt
            found = True; continue

        # --- ညီကို (၂၀ ကွက်) ---
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']):
            total += 20 * amt
            found = True; continue

        # --- စုံဘရိတ် (၅၀ ကွက်) ---
        if any(x in line for x in ['စုံဘရိတ်', 'စဘရိတ်', 'စုံbk']):
            total += 50 * amt
            found = True; continue

        # --- စစ / မမ / စမ / မစ (၂၅ ကွက်) ---
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစုံ']):
            total += 25 * amt * (2 if 'r' in line or 'အာ' in line else 1)
            found = True; continue

        # --- ကပ် / ကို (n1 * n2) ---
        if any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                total += (len(nums[0]) * len(nums[1])) * amt * (2 if 'r' in line or 'အာ' in line else 1)
                found = True; continue

        # --- ၂ လုံးတွဲ (ဒဲ့ / R / ဈေးကွဲ) ---
        nums = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
        if nums:
            r_val = re.search(r'r\s*(\d+)', line)
            if r_val: # ဈေးကွဲ 500R250
                r_amt = int(r_val.group(1))
                d_amt_match = re.search(r'(\d+)\s*r', line)
                d_amt = int(d_amt_match.group(1)) if d_amt_match else amt
                total += len(nums) * (d_amt + r_amt)
            elif 'r' in line or 'အာ' in line:
                total += len(nums) * amt * 2
            else:
                total += len(nums) * amt
            found = True

    return total if found else 0
