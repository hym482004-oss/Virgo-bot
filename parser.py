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
    lines = text.split('\n')
    total_sum = 0
    current_amt = 0
    valid_found = False

    # အောက်က amount ကို အပေါ်က ယူသုံးဖို့အတွက် အစီအစဉ်အတိုင်း သွားမယ်
    # ဒါပေမဲ့ စာကြောင်းတိုင်းမှာ amount ပါ၊ မပါ အရင်စစ်မယ်
    processed_lines = []
    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ['total', 'cash back', 'ကံကောင်းပါစေ']): continue
        
        amt_match = re.search(r'(\d+)$', line)
        line_amt = int(amt_match.group(1)) if amt_match else 0
        processed_lines.append({'text': line, 'amt': line_amt})

    # Amount မပါတဲ့ စာကြောင်းတွေအတွက် အောက်က amount ကို ရှာပေးတဲ့ logic
    for i in range(len(processed_lines)):
        if processed_lines[i]['amt'] == 0:
            for j in range(i + 1, len(processed_lines)):
                if processed_lines[j]['amt'] > 0:
                    processed_lines[i]['amt'] = processed_lines[j]['amt']
                    break

    for item in processed_lines:
        line = item['text']
        amt = item['amt']
        if amt == 0: continue

        # 1. ဒဲ့ နှင့် R (ဈေးကွဲစစ်ခြင်း)
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_val_match = re.search(r'r(\d+)', line)
            d_val_match = re.search(r'(\d+)r', line)
            
            d_amt = int(d_val_match.group(1)) if d_val_match else amt
            total_sum += len(numbers) * d_amt
            
            if r_val_match:
                total_sum += len(numbers) * int(r_val_match.group(1))
            elif 'r' in line:
                total_sum += len(numbers) * d_amt # R ဆိုရင် ဒဲ့ဈေးအတိုင်း တစ်ဆထပ်ပေါင်း
            valid_found = True
            continue

        # 2. ပတ်သီး / အပါ / Ch / P
        if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line)
            count = 20 if any(x in line for x in ['ပူးပို', '၂၀', '20', 'ပတ်ပူး']) else 19
            total_sum += (len(nums[:-1]) if len(nums) > 1 else 1) * count * amt
            valid_found = True

        # 3. အခွေ / အခွေပူး
        elif any(x in line for x in ['ခွေ', 'ခ']):
            nums = re.findall(r'\d', re.split(r'[ခခွေ]', line)[0])
            n = len(nums)
            if n > 1:
                total_sum += (n * n if any(x in line for x in ['ပူး', 'ခပ']) else n * (n-1)) * amt
                valid_found = True

    return total_sum if valid_found else 0
