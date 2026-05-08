import re

def get_market_data(text):
    text = text.lower()
    
    # MM Market (10%)
    if any(x in text for x in ['mm', 'Mm', 'MM']):
        return 0.10, "10%"
        
    # Global Market (3%)
    if any(x in text for x in ['glo', 'global', 'ဂလို']):
        return 0.03, "3%"
        
    # Dubai, Mega, Maxi, London, Lao, Landon (7%)
    # နင်ပေးထားတဲ့ Keywords အကုန် ဒီထဲထည့်ထားတယ်
    market_7pct = [
        'dubai', 'ဒူ', 'ဒူဘိုင်း', 'du', # Dubai
        'mega', 'me', 'မီ', 'မီဂါ',      # Mega
        'maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ', # Maxi
        'london', 'လန်လန်', 'လန်ဒန်', 'ld', 'landon', # London
        'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို', 'lao' # Lao
    ]
    
    if any(x in text for x in market_7pct):
        return 0.07, "7%"
        
    # ဘာမှမပါရင် Default အနေနဲ့ 7% ပဲ ထားပေးထားတယ်
    return 0.07, "7%"

def calculate_2d(text):
    # Symbol ရှင်းလင်းခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'စုစုပေါင်း', 'လက်ခံ']):
            continue
        
        # 1. Amount Detection (ဒဲ့ရော R ရော)
        r_price = 0
        normal_price = 0
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        if r_match:
            r_price = int(r_match.group(2))
            line_body = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_body)
            normal_price = int(norm_match.group(1)) if norm_match else 0
            prefix = line_body[:(norm_match.start() if norm_match else len(line_body))].strip()
        else:
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_price = int(all_nums[-1])
                prefix = re.sub(rf'\s?{normal_price}$', '', line).strip()
            else:
                prefix = line

        # 2. Cell Counting
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        line_cells = 0

        # Keywords Groups
        if any(x in line for x in ['ပတ်ပူးပို', 'ပါပူး', 'ပူးပို', 'ထိပ်ပိတ်']):
            line_cells = len(num_str) * 20
        elif any(x in line for x in ['ပတ်သီး', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ထိပ်', 'ပိတ်', 'bk', 'ဘရိတ်']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['ခွေ', 'ခ']):
            n = len(num_str)
            line_cells = (n * (n - 1)) if n > 1 else 0
        else:
            # ဒဲ့ဂဏန်း R logic (အပူးပါမကျန် ၂ ကွက်)
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for d in two_digits:
                    line_cells += 2 if is_r else 1
            else:
                line_cells = len(num_str) * (2 if is_r else 1)

        # 3. Final Multiplier
        total_price = normal_price + r_price
        if total_price > 10:
            grand_total += ((pending_cells + line_cells) * total_price)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
