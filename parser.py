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
import re

def calculate_bets(text):
    # သင်္ကေတတွေကို space ခြားပစ်မယ်
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total_sum = 0
    valid_found = False
    processed_data = []

    # Amount (ထိုးကြေး) ရှာပြီး အပေါ်စာကြောင်းတွေကို တွဲပေးမယ်
    for line in lines:
        l = line.lower()
        if any(x in l for x in ['total', 'cash', 'ကံကောင်း', '2d', 'du', 'me', 't=', 'တွက်']): continue
        
        amt_match = re.search(r'(\d+)$', l)
        amt = int(amt_match.group(1)) if amt_match else 0
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

        # --- ခွေ / အခွေ / ခ / ပူး (ခွေပူး) ---
        if any(x in line for x in ['ခွေ', 'ခ']):
            num_match = re.search(r'(\d{3,10})', line)
            if num_match:
                n = len(num_match.group(1))
                if any(x in line for x in ['ပူး', 'ခပ', 'အပူးပါ', 'အပူးအပြီးပါ']): count = n * n
                else: count = n * (n - 1)
                total_sum += count * amt
                valid_found = True; continue

        # --- ကပ် / ကို / အကပ် ---
        if any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                count = len(nums[0]) * len(nums[1])
                mult = 2 if any(x in line for x in ['r', 'အာ']) else 1
                total_sum += count * amt * mult
                valid_found = True; continue

        # --- ပတ်သီး / အပါ / ပါ / Ch / P ---
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်', 'ပတ်ပူး']):
                count = 20
            else: count = 19
            total_sum += len(nums) * count * amt
            valid_found = True; continue

        # --- ထိပ် / ဘရိတ် / ဆယ်ပြည့် / အပူး / ပါဝါ / နက္ခတ် / ညီကို ---
        # 385bk လိုမျိုး ကပ်ရေးတာကိုပါ တွက်မယ်
        if any(x in line for x in ['ထိပ်', 'ထ', 't', 'ဘရိတ်', 'bk', 'ဆယ်', 'အပူး', 'ပူး', 'ပဝ', 'pw', 'nk', 'နက', 'နခ']):
            nums = re.findall(r'\d', line.split('bk')[0] if 'bk' in line else line)
            count = len(nums) if len(nums) > 0 else 1
            total_sum += count * 10 * amt
            valid_found = True; continue
            
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']):
            total_sum += 20 * amt
            valid_found = True; continue

        # --- စစ / မမ / စမ / မစ / စုံစုံ / စုံမ / စုံဘရိတ် ---
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစုံ']):
            mult = 2 if any(x in line for x in ['r', 'အာ']) else 1
            total_sum += 25 * amt * mult
            valid_found = True; continue

        if 'ဘရိတ်' in line and any(x in line for x in ['စုံ', 'မ', 'စ', 'စုံbk', 'မbk']):
            total_sum += 50 * amt
            valid_found = True; continue

        # --- ဒဲ့ နှင့် R (ဈေးကွဲစစ်ခြင်း) ---
        numbers = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
        if numbers:
            r_amt_match = re.search(r'r(\d+)', line)
            if r_amt_match: # 500R250
                d_val_match = re.search(r'(\d+)r', line)
                d_amt = int(d_val_match.group(1)) if d_val_match else amt
                r_amt = int(r_amt_match.group(1))
                total_sum += len(numbers) * (d_amt + r_amt)
            elif any(x in line for x in ['r', 'အာ']): # R (၂ ဆ)
                total_sum += len(numbers) * amt * 2
            else: # ဒဲ့ (၁ ဆ)
                total_sum += len(numbers) * amt
            valid_found = True

    return total_sum if valid_found else 0
