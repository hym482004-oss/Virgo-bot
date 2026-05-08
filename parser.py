import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    # Error မတက်အောင် ဘာမှမပါရင်လည်း default 0.07 ပေးထားမည်
    return 0.07, "7%"

def calculate_bets(text):
    for s in ['*', '-', "'", '/', '.', '=', '။']:
        text = text.replace(s, ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False
    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        price_diff = re.search(r'(\d+)\s*r\s*(\d+)', line)
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        d_amt = int(price_diff.group(1)) if price_diff else int(all_nums[-1])
        r_amt = int(price_diff.group(2)) if price_diff else d_amt
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        line_valid = False
        # (6) အပူးပါခွေ / ခွေပူး
        if any(x in line for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ', 'အပူးအပြီးပါ']) and any(x in line for x in ['ခွေ', 'ခ']):
            n_match = re.search(r'(\d{3,10})', line)
            if n_match:
                n = len(n_match.group(1))
                total += (n * n) * d_amt
                line_valid = True
        # (5) ခွေ
        elif any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            n_match = re.search(r'(\d{3,10})', line)
            if n_match:
                n = len(n_match.group(1))
                total += (n * (n - 1)) * d_amt
                line_valid = True
        # (9) ကပ် / ကို
        if any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            groups = re.findall(r'\d+', line.split(all_nums[-1])[0])
            if len(groups) >= 2:
                count = len(groups[0]) * len(groups[1])
                total += (count * d_amt) + (count * r_amt if is_r else 0)
                line_valid = True
        # (1) ၁၀ ကွက်တန်များ
        ten_keys = ['ပါဝါ', 'pw', 'power', 'ပဝ', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ထ', 'top', 't', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']
        for k in ten_keys:
            if k in line:
                total += 10 * d_amt
                line_valid = True
        # (11) ၂၀ ကွက်တန်များ
        twenty_keys = ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']
        if any(x in line for x in twenty_keys):
            total += 20 * d_amt
            line_valid = True
        # (10) ၅၀ ကွက်တန်
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            total += 50 * d_amt
            line_valid = True
        # (8) ၂၅ ကွက်တန်
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစုံ']):
            total += 25 * d_amt * (2 if is_r else 1)
            line_valid = True
        # (4) ၁၉ ကွက်တန် (ပတ်သီး)
        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ', 'ch', 'p']) and not any(x in line for x in ['ပတ်ပူး', 'ပူးပို']):
            n_match = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            total += (len(n_match) if n_match else 1) * 19 * d_amt
            line_valid = True
        # (7) ၅ ကွက်တန်
        if any(x in line for x in ['စုံပူး', 'မပူး']):
            total += 5 * d_amt
            line_valid = True
        # (2, 3) ဒဲ့ / R
        if not line_valid:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', line)
            if two_digits:
                total += len(two_digits) * d_amt
                if is_r: total += len(two_digits) * r_amt
                line_valid = True
        if line_valid: found = True
    return total if found else 0
