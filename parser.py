import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    return 0.07, None 

def calculate_bets(text):
    # သင်္ကေတတွေကို space ခြားပြီး စာကြောင်းတွေကို သန့်စင်မယ်
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total_sum = 0
    valid_found = False
    processed_data = []

    # 1. Amount (ထိုးကြေး) ရှာဖွေခြင်း Logic
    for line in lines:
        l = line.lower()
        if any(x in l for x in ['total', 'cash', 'ကံကောင်း', '2d', 'du', 'me', 't=', 'တွက်']): continue
        
        # စာကြောင်းအဆုံးမှာရှိတဲ့ ဂဏန်းကို ထိုးကြေးအဖြစ် ယူမယ်
        amt_match = re.findall(r'\d+', l)
        amt = int(amt_match[-1]) if amt_match else 0
        processed_data.append({'txt': l, 'amt': amt})

    # Amount မပါတဲ့ စာကြောင်းတွေအတွက် အောက်က amount ကို လှမ်းယူမယ်
    for i in range(len(processed_data)):
        if processed_data[i]['amt'] == 0:
            for j in range(i + 1, len(processed_data)):
                if processed_data[j]['amt'] > 0:
                    processed_data[i]['amt'] = processed_data[j]['amt']
                    break

    # 2. Keyword နဲ့ ဂဏန်းများ တွက်ချက်ခြင်း Logic
    for item in processed_data:
        line = item['txt']
        amt = item['amt']
        if amt == 0: continue

        # --- ခွေ / ခွေပူး (၃ လုံးနဲ့ အထက်) ---
        if any(x in line for x in ['ခွေ', 'ခ']):
            num_match = re.search(r'(\d{3,10})', line)
            if num_match:
                n = len(num_match.group(1))
                count = n * n if any(x in line for x in ['ပူး', 'ခပ', 'အပူးပါ']) else n * (n - 1)
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
            # ပတ်ပူး / ၂၀ ကွက် Formula
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်', 'ပတ်ပူး']) else 19
            total_sum += len(nums) * count * amt
            valid_found = True; continue

        # --- ၁၀ ကွက်တန် Keyword များ (ထိပ် / ဘရိတ် / အပူး / ပါဝါ / နက္ခတ်) ---
        if any(x in line for x in ['ထိပ်', 'ထ', 't', 'ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ပဝ', 'pw', 'nk','နတ်ခတ်','နက်ခက်', 'နက', 'နခ', 'ဆယ်']):
            nums = re.findall(r'\d', line.split('bk')[0] if 'bk' in line else line)
            count = len(nums) if len(nums) > 0 else 1
            total_sum += count * 10 * amt
            valid_found = True; continue

        # --- ညီကို / စစ / မမ / စမ / မစ ---
        if any(x in line for x in ['ညီကို', 'ညီအကို']):
            total_sum += 20 * amt
            valid_found = True; continue
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
            mult = 2 if any(x in line for x in ['r', 'အာ']) else 1
            total_sum += 25 * amt * mult
            valid_found = True; continue

        # --- ၂ လုံးတွဲ ဒဲ့ / R (အဓိက ပြင်ဆင်ထားသောအပိုင်း) ---
        # စာကြောင်းထဲက ၂ လုံးတွဲ ဂဏန်းအားလုံးကို ရှာမယ်
        numbers = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
        if numbers:
            # R ပါ၊ မပါ စစ်မယ်
            is_r = any(x in line for x in ['r', 'အာ'])
            
            # ဈေးကွဲ ရှိ၊ မရှိ စစ်မယ် (ဥပမာ 500R250)
            r_val_match = re.search(r'r\s*(\d+)', line)
            
            if r_val_match:
                r_amt = int(r_val_match.group(1))
                # ဒဲ့ဈေးကို ရှာမယ် (R ရဲ့ ရှေ့က ဂဏန်း)
                d_amt_match = re.search(r'(\d+)\s*r', line)
                d_amt = int(d_amt_match.group(1)) if d_amt_match else amt
                total_sum += len(numbers) * (d_amt + r_amt)
            elif is_r:
                # R တစ်လုံးတည်းဆိုရင် ၂ ဆ (ဒဲ့ ၅၀၀ + အာ ၅၀၀)
                total_sum += len(numbers) * amt * 2
            else:
                # ဒဲ့ သီးသန့်ဆိုရင် ၁ ဆ
                total_sum += len(numbers) * amt
            valid_found = True

    return total_sum if valid_found else 0
