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
    total = 0
    found = False
    pending_units = 0 

    for i, line in enumerate(lines):
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # Amount (R ပါသော ဂဏန်း သို့မဟုတ် ၃ လုံးနှင့်အထက်)
        amt_match = re.search(r'(?:r|R)?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        line_unit = 0
        is_r = any(x in line.lower() for x in ['r', 'အာ', 'ာ'])

        # Multi-line context အတွက်
        context_text = lines[i-1] + " " + line if i > 0 else line

        # 1. ၅၀ ကွက်တန် - စုံဘရိတ်/မဘရိတ်
        if any(x in prefix for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_unit = 50
        
        # 2. ၂၅ ကွက်တန် - စစ/မမ/စုံစုံ
        elif any(x in prefix for x in ['စစ', 'မမ', 'စုံစုံ', 'စုံမ', 'စမ', 'မစ']):
            line_unit = 25 * (2 if is_r else 1)

        # 3. ၂၀ ကွက်တန် - ညီကို/ပတ်ပူး/ထိပ်ပိတ်
        elif any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_unit = 20

        # 4. ၁၉ ကွက်တန် - ပတ်သီး/အပါ/ပါ/ch/p
        elif any(x in prefix for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']) and 'ပတ်ပူး' not in prefix:
            nums_in_prefix = re.findall(r'\d', prefix)
            line_unit = len(nums_in_prefix) * 19 if nums_in_prefix else 19

        # 5. ၁၀ ကွက်တန် - ပါဝါ/နက္ခတ်/ဘရိတ်/ထိပ်/ပိတ်/အပူး/ဆယ်ပြည့်
        elif any(x in prefix for x in ['ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'နက', 'နခ', 'nk', 'ဘရိတ်', 'bk', 'ထိပ်', 'top', 't', 'ပိတ်', 'နောက်', 'အနောက်', 'အပူးစုံ', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်']):
            nums_in_prefix = re.findall(r'\d', prefix)
            multiplier = len(nums_in_prefix) if nums_in_prefix else 1
            line_unit = multiplier * 10

        # 6. ၅ ကွက်တန် - စုံပူး/မပူး
        elif any(x in prefix for x in ['စုံပူး', 'မပူး', 'စပူး']):
            line_unit = 5

        # 7. ခွေပူး (N x N)
        elif any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = n * n if n > 0 else 0

        # 8. ခွေ (N x N-1)
        elif any(x in prefix for x in ['ခွေ', 'ခ', 'အခွေ']):
            n = len("".join(re.findall(r'\d+', prefix)))
            line_unit = (n * (n - 1)) if n > 0 else 0

        # 9. ကပ်/ကို (a x b)
        elif any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            groups = re.findall(r'(\d+)', prefix)
            if len(groups) >= 2:
                line_unit = len(groups[0]) * len(groups[1])
                if is_r: line_unit *= 2
        
        # 10. ဒဲ့ သို့မဟုတ် Symbol (- = ဒဲ့)
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit = len(two_digits) * (2 if is_r else 1)
            elif re.search(r'\d', prefix):
                line_unit = 1 * (2 if is_r else 1)

        # တွက်ချက်ခြင်း
        if amt > 0:
            total += (pending_units + line_unit) * amt
            pending_units = 0
            found = True
        else:
            pending_units += line_unit

    return total if found else 0
