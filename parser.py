import re

def get_market_rate(text):
    t = text.lower()
    # Market rates based on keywords
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # Clean up common delimiters but keep essential markers
    text = text.replace('=', ' ').replace('-', ' ').replace(',', ' ').replace('။', ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    
    grand_total = 0
    pending_units = 0 

    for line in lines:
        # Skip summary lines
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း', 'ရှင်း']): continue
        
        # 1. Identify Amount (Usually at the end of the line)
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        # 2. Extract Numbers for counting
        num_blocks = re.findall(r'\d+', prefix)
        full_digit_string = "".join(num_blocks)
        count = len(full_digit_string)
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        
        line_unit = 0

        # 3. Apply Group Rules based on Keywords
        # Group 11 (50 Units)
        if any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_unit = 50
        # Group 9 (25 Units)
        elif any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စုံစူံ', 'စူံစုံ']):
            line_unit = 25
        # Group 1 (20 Units)
        elif any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20
        # Group 5 (19 Units)
        elif any(x in prefix for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_unit = len(num_blocks) * 19 if num_blocks else 19
        # Group 2 (10 Units)
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်စီး', 'ထိပ်', 'ထ', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            line_unit = len(num_blocks) * 10 if num_blocks else 10
        # Group 8 (5 Units)
        elif any(x in prefix for x in ['စပူး', 'စုံပူး', 'မပူး']):
            line_unit = 5
        # Group 10 (Kap/Ko Logic)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_unit = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_unit *= 2
        # Group 7 (Kway Puu: n*n)
        elif any(x in prefix for x in ['အပူးပါခွေ', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခွေပူး', 'အခွေပူး', 'ခပ']):
            line_unit = count * count
        # Group 6 (Kway: n*(n-1))
        elif any(x in prefix for x in ['ခွေ', 'အခွေ', 'ခ']):
            line_unit = count * (count - 1)
        # Group 3/4 (Direct or R)
        else:
            # Check for 2-digit pairs
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            else:
                line_unit = count * (2 if is_r else 1)

        # 4. Final Aggregation
        if amt > 0:
            grand_total += (pending_units + line_unit) * amt
            pending_units = 0
        else:
            pending_units += line_unit

    return grand_total, []
