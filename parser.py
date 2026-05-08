import re

def get_market_data(text):
    text = text.lower()
    if any(x in text for x in ['mm']): return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    if any(x in text for x in ['du', 'dubai', 'ဒူ', 'me', 'mega', 'မီ', 'max', 'maxi', 'မက်', 'ld', 'london', 'lao', 'laos']): 
        return 0.07, "7%"
    return 0.07, "7%" # Default 7%

def calculate_2d(text):
    lines = text.lower().split('\n')
    grand_total = 0
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ']): continue
        
        # Split separators: space, -, =, *, /, ., :, 
        parts = re.split(r'[ \-=*/.:]+', line)
        parts = [p for p in parts if p]
        
        # Amount detection (Last number and R amount)
        r_amount = 0
        normal_amount = 0
        
        # Check for R amount (e.g., R250 or 500R250)
        r_match = re.search(r'r(\d+)', line)
        if r_match:
            r_amount = int(r_match.group(1))
            # Remove the R part to find normal amount
            line_no_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_no_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
        else:
            # No R specifically marked with amount, take last number
            last_num_match = re.findall(r'\d+', line)
            if last_num_match:
                normal_amount = int(last_num_match[-1])
                if any(x in line for x in ['r', 'အာ']):
                    r_amount = normal_amount

        # Counting Logic
        cells = 0
        is_r = any(x in line for x in ['r', 'အာ'])
        
        # 1. Fixed Groups (50, 25, 20, 19, 10, 5)
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            cells = 50
        elif any(x in line for x in ['စမ', 'စစ', 'မမ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            cells = 25 * (2 if is_r else 1)
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန်', 'ထပ်', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            cells = 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'p', 'ch']):
            nums = re.findall(r'\d+', prefix_only(line, normal_amount, r_amount))
            cells = len("".join(nums)) * 19
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'အပူး', 'အပူးစုံ', 'ပါဝါ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက်', 'နခ']):
            cells = 10
        elif any(x in line for x in ['ထိပ်', 'ထ', 'top', 't', 'ပိတ်', 'အပိတ်', 'နောက်', 'အနောက်', 'ဘရိတ်', 'bk']):
            nums = re.findall(r'\d+', prefix_only(line, normal_amount, r_amount))
            cells = len("".join(nums)) * 10
        elif any(x in line for x in ['စုံပူး', 'မပူး', 'စပူး']):
            cells = 5
            
        # 2. Variable Groups (ခွေ, ခွေပူး, ကပ်)
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ပူး']) and 'ပတ်ပူး' not in line:
            n = len("".join(re.findall(r'\d+', prefix_only(line, normal_amount, r_amount))))
            cells = n * n
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len("".join(re.findall(r'\d+', prefix_only(line, normal_amount, r_amount))))
            cells = n * (n - 1)
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            groups = re.findall(r'\d+', prefix_only(line, normal_amount, r_amount))
            if len(groups) >= 2:
                cells = len(groups[0]) * len(groups[1])
                if is_r: cells *= 2
        
        # 3. Direct / R (ဂဏန်းအလုံးရေအလိုက်)
        else:
            nums = re.findall(r'\d{2}', prefix_only(line, normal_amount, r_amount))
            if not nums: # Single digit check
                single = re.findall(r'^\d{1}$', prefix_only(line, normal_amount, r_amount))
                if single: return "error"
                nums = re.findall(r'\d', prefix_only(line, normal_amount, r_amount))
            
            cells = len(nums)
            # တွက်ချက်မှု - Normal နဲ့ R ခွဲတွက်ခြင်း
            line_total = (cells * normal_amount) + (cells * r_amount if is_r and r_amount > 0 else 0)
            grand_total += line_total
            continue # Already summed for Direct/R

        # For Keywords with single amount
        grand_total += cells * normal_amount

    return grand_total

def prefix_only(line, norm, r):
    # Amount တွေကို ဖယ်ပြီး ကျန်တဲ့ စာသားနဲ့ ဂဏန်းတွေကိုပဲ ယူတယ်
    clean = line.replace(str(norm), "").replace(str(r), "").replace('r', '').replace('အာ', '')
    return clean
