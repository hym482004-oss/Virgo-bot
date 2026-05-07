import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    return 0.07, None 

def calculate_bets(text):
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total_sum = 0
    valid_found = False
    processed_data = []

    for line in lines:
        l = line.lower()
        if any(x in l for x in ['total', 'cash', 'ကံကောင်း', '2d', 'du', 'me']): continue
        amt_match = re.findall(r'\d+', l)
        amt = int(amt_match[-1]) if amt_match else 0
        processed_data.append({'txt': l, 'amt': amt})

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

        # ခွေ / ခွေပူး
        if any(x in line for x in ['ခွေ', 'ခ']):
            num_match = re.search(r'(\d{3,10})', line)
            if num_match:
                n = len(num_match.group(1))
                count = n * n if any(x in line for x in ['ပူး', 'ခပ', 'အပူးပါ']) else n * (n - 1)
                total_sum += count * amt
                valid_found = True; continue

        # ကပ် / ကို
        if any(x in line for x in ['ကပ်', 'ကို']):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                total_sum += (len(nums[0]) * len(nums[1])) * amt * (2 if 'r' in line or 'အာ' in line else 1)
                valid_found = True; continue

        # ပတ်သီး / ၂၀ ကွက်
        if any(x in line for x in ['ပတ်', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ပတ်ပူး']) else 19
            total_sum += len(nums) * count * amt
            valid_found = True; continue

        # ၁၀ ကွက်တန်များ (385bk500 လိုမျိုးအတွက်ပါ ပြင်ထားတယ်)
        if any(x in line for x in ['ထိပ်', 'ထ', 't', 'ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ပဝ', 'nk', 'ဆယ်']):
            nums_part = line.split('bk')[0] if 'bk' in line else line
            nums = re.findall(r'\d', nums_part)
            count = len(nums) if len(nums) > 0 else 1
            total_sum += count * 10 * amt
            valid_found = True; continue

        # ၂ လုံးတွဲ ဒဲ့ / R / ဈေးကွဲ (500R250)
        numbers = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
        if numbers:
            r_val_match = re.search(r'r\s*(\d+)', line)
            if r_val_match:
                r_amt = int(r_val_match.group(1))
                d_amt_match = re.search(r'(\d+)\s*r', line)
                d_amt = int(d_amt_match.group(1)) if d_amt_match else amt
                total_sum += len(numbers) * (d_amt + r_amt)
            elif any(x in line for x in ['r', 'အာ']):
                total_sum += len(numbers) * amt * 2
            else:
                total_sum += len(numbers) * amt
            valid_found = True

    return total_sum if valid_found else 0
