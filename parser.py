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
    # စာလုံးပေါင်းအမှားနဲ့ သင်္ကေတများ ရှင်းလင်းခြင်း
    text = text.lower().replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    total = 0
    found = False
    
    # ညီကို တွက်နည်း (Fixed Patterns)
    bro_patterns = ['01','12','23','34','45','56','67','78','89','90','10','21','32','43','54','65','76','87','98','09']
    # အပူး patterns
    double_patterns = ['00','11','22','33','44','55','66','77','88','99']
    # ပါဝါ patterns
    power_patterns = ['05','50','16','61','27','72','38','83','49','94']
    # နက္ခတ် patterns
    nk_patterns = ['07','70','18','81','24','42','35','53','69','96']

    # Amount ရှာဖွေခြင်း
    processed_data = []
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

        # --- ၁။ ညီကို (Bro) ---
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']):
            total += len(bro_patterns) * amt
            found = True; continue

        # --- ၂။ အပူး / အပူးစုံ (Double) ---
        if any(x in line for x in ['အပူး', 'ပူး']) and not any(x in line for x in ['ခွေ', 'ပတ်']):
            total += len(double_patterns) * amt
            found = True; continue

        # --- ၃။ ပါဝါ (Power) ---
        if any(x in line for x in ['ပါဝါ', 'pw', 'ပဝ']):
            total += len(power_patterns) * amt
            found = True; continue

        # --- ၄။ နက္ခတ် (NK) ---
        if any(x in line for x in ['နက္ခတ်', 'nk', 'နက', 'နခ']):
            total += len(nk_patterns) * amt
            found = True; continue

        # --- ၅။ ခွေပူး / အခွေပူး ---
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အခွေပူး']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * n) * amt
                found = True; continue

        # --- ၆။ ခွေ / အခွေ ---
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = re.search(r'(\d{3,10})', line)
            if nums:
                n = len(nums.group(1))
                total += (n * (n - 1)) * amt
                found = True; continue

        # --- ၇။ ပတ်သီး / ၂၀ ကွက် ---
        if any(x in line for x in ['ပတ်', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ပတ်ပူး']) else 19
            total += (len(nums) if nums else 1) * count * amt
            found = True; continue

        # --- ၈။ ထိပ် / ဘရိတ် / ဆယ်ပြည့် ---
        if any(x in line for x in ['ထိပ်', 'ထ', 't', 'ဘရိတ်', 'bk', 'ဆယ်']):
            nums_part = line.split('bk')[0] if 'bk' in line else line
            nums = re.findall(r'\d', nums_part)
            total += (len(nums) if nums else 1) * 10 * amt
            found = True; continue

        # --- ၉။ စစ / မမ / စုံစုံ ---
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
            total += 25 * amt * (2 if 'r' in line or 'အာ' in line else 1)
            found = True; continue

        # --- ၁၀။ ၂ လုံးတွဲ ဒဲ့ / R ---
        nums = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
        if nums:
            if 'r' in line or 'အာ' in line:
                total += len(nums) * amt * 2
            else:
                total += len(nums) * amt
            found = True

    return total if found else 0
