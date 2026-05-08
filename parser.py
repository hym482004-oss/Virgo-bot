import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    grand_total = 0
    line_details = []
    pending_items = [] # Amount မပါခင် စုထားမည့် အကွက်များ

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း']): continue
        
        # 1. Amount ရှာဖွေခြင်း
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        current_unit = 0
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        num_blocks = re.findall(r'\d+', prefix)
        count = len("".join(num_blocks))

        # 2. Priority Keyword Mapping
        # Group 1 (20 Units)
        if any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            current_unit = 20
        # Group 2 (10 Units)
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်စီး', 'ထိပ်', 'ထ', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            current_unit = len(num_blocks) * 10 if num_blocks else 10
        # Group 5 (19 Units)
        elif any(x in prefix for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            current_unit = count * 19 if count > 0 else 19
        # Group 7 (NxN)
        elif any(x in prefix for x in ['အပူးပါခွေ', 'ပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခွေပူး', 'အခွေပူး', 'ခပ']):
            current_unit = count * count
        # Group 6 (NxN-1)
        elif any(x in prefix for x in ['ခွေ', 'အခွေ', 'ခ']):
            current_unit = count * (count - 1)
        # Group 11 (50 Units)
        elif any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            current_unit = 50
        # Group 9 (25 Units)
        elif any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စုံစူံ', 'စူံစုံ']):
            current_unit = 25
        # Group 8 (5 Units)
        elif any(x in prefix for x in ['စပူး', 'စုံပူး', 'မပူး']):
            current_unit = 5
        # Group 10 (AxB)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                current_unit = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: current_unit *= 2
        # Default (Direct / R)
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                current_unit = len(two_digits) * (2 if is_r else 1)
            elif count > 0:
                current_unit = count * (2 if is_r else 1)

        # 3. Processing & Summing
        if amt > 0:
            total_unit = pending_units + current_unit
            line_total = total_unit * amt
            grand_total += line_total
            line_details.append(f"{line} = {line_total:,}")
            pending_units = 0
        else:
            pending_units += current_unit
            line_details.append(line)

    return grand_total, line_details
