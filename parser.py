import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # Delimiters ကို ရှင်းလင်းခြင်း (- နှင့် = ကို space ပြောင်း၍ တွက်ချက်ရလွယ်အောင်လုပ်သည်)
    text = text.replace('-', ' ').replace('=', ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    
    grand_total = 0
    line_results = []
    pending_units = 0 

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း']): continue
        
        # 1. Amount ရှာဖွေခြင်း (စာကြောင်းအဆုံးမှ ဂဏန်း)
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        # 2. Number Blocks ခွဲထုတ်ခြင်း
        num_blocks = re.findall(r'\d+', prefix)
        count = len("".join(num_blocks))
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        
        line_unit = 0

        # 3. Keyword Group Rules (Specification အတိုင်း)
        
        # [GROUP 11] (50 blocks)
        if any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_unit = 50
        # [GROUP 9] (25 blocks)
        elif any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စုံစူံ', 'စူံစုံ']):
            line_unit = 25
        # [GROUP 1] (20 blocks)
        elif any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20
        # [GROUP 5] (19 blocks)
        elif any(x in prefix for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_unit = 19
        # [GROUP 2] (10 blocks)
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်စီး', 'ထိပ်', 'ထ', 'top', 't', 'အပိတ်', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            line_unit = len(num_blocks) * 10 if num_blocks else 10
        # [GROUP 8] (5 blocks)
        elif any(x in prefix for x in ['စပူး', 'စုံပူး', 'မပူး']):
            line_unit = 5
        # [GROUP 10] (ကပ်/ကို)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_unit = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_unit *= 2
        # [GROUP 7] (ခွေပူး - count x count)
        elif any(x in prefix for x in ['အပူးပါခွေ', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခွေပူး', 'အခွေပူး', 'ခပ']):
            line_unit = count * count
        # [GROUP 6] (ခွေ - count x count-1)
        elif any(x in prefix for x in ['ခွေ', 'အခွေ', 'ခ']):
            line_unit = count * (count - 1)
        # [GROUP 3 & 4] (Direct / R)
        else:
            # 2 လုံးတွဲများကို အရင်ရှာသည်
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            else:
                line_unit = count * (2 if is_r else 1)

        # 4. Calculation Process
        if amt > 0:
            current_total = (pending_units + line_unit) * amt
            grand_total += current_total
            line_results.append(f"{line} = {current_total:,}")
            pending_units = 0
        else:
            pending_units += line_unit
            line_results.append(line)

    return grand_total, line_results
