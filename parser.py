import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို']): return 0.07, "7%"
    if any(x in t for x in ['london', 'လန်လန်', 'လန်ဒန်', 'ld']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    return 0.07, None 

def calculate_bets(text):
    # စာလုံးပေါင်း အမှားအယွင်းခံနိုင်အောင် သန့်စင်ခြင်း
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    total_sum = 0
    valid_found = False

    # စာကြောင်းတစ်ခုချင်းစီကို Processing လုပ်မယ်
    processed_data = []
    for line in lines:
        l = line.lower()
        if any(x in l for x in ['total', 'cash back', 'ကံကောင်းပါစေ']): continue
        
        # Amount ရှာခြင်း (စာကြောင်းအဆုံးက ဂဏန်း)
        amt_match = re.search(r'(\d+)$', l)
        amt = int(amt_match.group(1)) if amt_match else 0
        processed_data.append({'original': l, 'amt': amt})

    # အောက်က amount ကို အပေါ်က ယူသုံးတဲ့ Logic
    for i in range(len(processed_data)):
        if processed_data[i]['amt'] == 0:
            for j in range(i + 1, len(processed_data)):
                if processed_data[j]['amt'] > 0:
                    processed_data[i]['amt'] = processed_data[j]['amt']
                    break

    for item in processed_data:
        line = item['original']
        amt = item['amt']
        if amt == 0: continue

        # --- တွက်ချက်မှု Logic များ ---
        
        # 1. ကပ် / ကို (e.g. 234ကို678ကပ်)
        if any(x in line for x in ['ကပ်', 'ကို']):
            nums = re.findall(r'\d+', line)
            if len(nums) >= 2:
                count = len(nums[0]) * len(nums[1])
                mult = 2 if 'r' in line or 'အာ' in line else 1
                total_sum += count * amt * mult
                valid_found = True; continue

        # 2. ပတ်သီး / အပါ / ပါ / Ch / P
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            # ပတ်ပူး / ၂၀ ကွက် စစ်ခြင်း
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']) else 19
            total_sum += len(nums) * count * amt
            valid_found = True; continue

        # 3. ထိပ် / ဘရိတ် / ဆယ်ပြည့် / အပူး / ပါဝါ / နက္ခတ် (၁၀ ကွက်တန်များ)
        ten_keys = ['ထိပ်', 'ထ', 'top', 't', 'ဘရိတ်', 'bk', 'ဆယ်', 'အပူး', 'ပူး', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk']
        if any(x in line for x in ten_keys):
            nums = re.findall(r'\d', line)
            count = len(nums) if len(nums) > 0 else 1
            total_sum += count * 10 * amt
            valid_found = True; continue

        # 4. ညီကို (၂၀ ကွက်)
        if 'ညီကို' in line or 'ညီအကို' in line:
            total_sum += 20 * amt
            valid_found = True; continue

        # 5. စစ / မမ / စမ / မစ (၂၅ ကွက်)
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
            mult = 2 if 'r' in line or 'အာ' in line else 1
            total_sum += 25 * amt * mult
            valid_found = True; continue

        # 6. စုံဘရိတ် / မဘရိတ် (၅၀ ကွက်)
        if 'ဘရိတ်' in line and any(x in line for x in ['စုံ', 'မ']):
            total_sum += 50 * amt
            valid_found = True; continue

        # 7. ခွေ / အခွေ / ခ
        if any(x in line for x in ['ခွေ', 'ခ']):
            nums = re.findall(r'\d', line.split('ခ')[0])
            n = len(nums)
            if n > 1:
                if any(x in line for x in ['ပူး', 'အပူးပါ']): # ခွေပူး (n*n)
                    total_sum += (n * n) * amt
                else: # ခွေ (n * n-1)
                    total_sum += (n * (n - 1)) * amt
                valid_found = True; continue

        # 8. ဒဲ့ နှင့် R (ဈေးကွဲ 500R250 ကိုပါ တွက်သည်)
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_amt_match = re.search(r'r(\d+)', line)
            # ဈေးကွဲရှိရင် (e.g. 500R250)
            if r_amt_match:
                d_amt = int(re.search(r'(\d+)r', line).group(1)) if re.search(r'(\d+)r', line) else amt
                r_amt = int(r_amt_match.group(1))
                total_sum += len(numbers) * (d_amt + r_amt)
            # R ပဲ ပါရင် (၂ ဆ)
            elif 'r' in line or 'အာ' in line:
                total_sum += len(numbers) * amt * 2
            # ဒဲ့ ပဲ ဆိုရင် (၁ ဆ)
            else:
                total_sum += len(numbers) * amt
            valid_found = True

    return total_sum if valid_found else 0
