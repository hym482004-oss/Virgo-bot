import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Price Detection (ဒဲ့ဈေးရော R ဈေးရော)
        r_price = 0
        normal_price = 0
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        if r_match:
            r_price = int(r_match.group(2))
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_price = int(norm_match.group(1)) if norm_match else 0
            prefix = line_pre_r[:(norm_match.start() if norm_match else len(line_pre_r))].strip()
        else:
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_price = int(all_nums[-1])
                prefix = re.sub(rf'\s?{normal_price}$', '', line).strip()
            else:
                prefix = line

        # 2. Cell Counting Logic
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        line_cells = 0

        # Keywords Checking
        if any(x in line for x in ['ပတ်ပူးပို', 'ပါပူး', 'ပူးပို', 'ထိပ်ပိတ်']):
            line_cells = len(num_str) * 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ထိပ်စီး', 'ထိပ်', 'top', 't ', 'အပိတ်', 'ပိတ်', 'နောက်', 'န', 'bk', 'ဘရိတ်']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_cells = 25
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'ပူး', 'အပူး', 'puu', 'ပုး', 'အပူးစုံ']):
            line_cells = 10
        elif any(x in line for x in ['ညီအစ်ကို', 'ညီကို', 'ညီအကို', 'ညီကိုး', 'ပတ်ပူး', 'ပတ်အကွက်20']):
            line_cells = 20
        elif any(x in line for x in ['စပူး', 'စုံပူး', 'မပူး']):
            line_cells = 5
        elif any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူးပါ']):
            line_cells = len(num_str) ** 2
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(num_str)
            line_cells = n * (n - 1) if n > 1 else 0
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_cells = len(num_blocks[0]) * len(num_blocks[1])
        else:
            # ဒဲ့ဂဏန်းများအတွက် (R ပါက အပူးပါမကျန် ၂ ကွက်တွက်သည်)
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for digit in two_digits:
                    line_cells += 2 if is_r else 1
            else:
                line_cells = len(num_str) * (2 if is_r else 1)

        # 3. Final Multiplier (Price ပေါင်းပြီးမှ အကွက်ရေနှင့်မြှောက်)
        total_price = normal_price + r_price
        
        if total_price > 10: 
            grand_total += ((pending_cells + line_cells) * total_price)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
