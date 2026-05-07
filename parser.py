import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'me', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို']): return 0.07, "7%"
    if any(x in t for x in ['london', 'လန်လန်', 'လန်ဒန်', 'ld']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    return 0.07, None 

def calculate_bets(text):
    lines = text.split('\n')
    lines.reverse()
    
    total_sum = 0
    current_amt = 0
    valid_found = False

    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ['2d', 'total', 't=', 'cashback', 'mega', 'du', 'mm']): continue

        amt_match = re.search(r'(\d+)$', line)
        if amt_match:
            current_amt = int(amt_match.group(1))
        
        if current_amt == 0: continue

        # 1. ပတ်သီး / အပါ / Ch / P (၁၉ သို့မဟုတ် ၂၀ ကွက်)
        if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ပတ်ပူး']) else 19
            total_sum += len(nums[:-1] if len(nums) > 1 else [1]) * count * current_amt
            valid_found = True
            continue

        # 2. အကပ် / ကို
        if any(x in line for x in ['ကပ်', 'ကို']):
            parts = re.findall(r'\d+', line)
            if len(parts) >= 2:
                base_count = len(parts[0]) * len(parts[1])
                r_val = re.search(r'r(\d+)', line)
                d_val = re.search(r'(\d+)r', line)
                d_amt = int(d_val.group(1)) if d_val else current_amt
                total_sum += base_count * d_amt
                if r_val: total_sum += base_count * int(r_val.group(1))
                elif 'r' in line: total_sum += base_count * d_amt
                valid_found = True
            continue

        # 3. အခွေ / အခွေပူး / ခပ
        if any(x in line for x in ['ခွေ', 'ခ']):
            nums_part = re.split(r'[ခခွေ]', line)[0]
            nums = re.findall(r'\d', nums_part)
            n = len(nums)
            if n > 1:
                if any(x in line for x in ['ပူး', 'ခပ']): total_sum += (n * n * current_amt)
                else: total_sum += (n * (n - 1) * current_amt)
                valid_found = True
            continue

        # 4. ၁၀ ကွက်တန် Keyword များ
        ten_keys = ['ထိပ်', 'ထ', 'top', 't', 'ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ဆယ်', 'pw', 'nk']
        if any(x in line for x in ten_keys):
            nums = re.findall(r'\d', line.split('ထိပ်')[0] if 'ထိပ်' in line else line)
            total_sum += (len(nums[:-1]) if len(nums) > 1 else 1) * 10 * current_amt
            valid_found = True
            continue

        # 5. ဒဲ့ နှင့် R (ဈေးကွဲ 600R400 ပါဝင်သည်)
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_val = re.search(r'r(\d+)', line)
            d_val = re.search(r'(\d+)r', line)
            d_amt = int(d_val.group(1)) if d_val else current_amt
            total_sum += len(numbers) * d_amt
            if r_val: total_sum += len(numbers) * int(r_val.group(1))
            elif 'r' in line: total_sum += len(numbers) * d_amt
            valid_found = True

    return total_sum if valid_found else 0
