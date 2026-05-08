import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # Separators များရှင်းလင်းခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Amount Detection (R/အာ Logic)
        r_amount = 0
        normal_amount = 0
        # R အုပ်စု Pattern ကို သေချာပြန်ပြင်ထားတယ်
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        
        if r_match:
            r_amount = int(r_match.group(2))
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
            prefix = line_pre_r[:(norm_match.start() if norm_match else len(line_pre_r))].strip()
        else:
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_amount = int(all_nums[-1])
                if any(x in line for x in ['r', 'အာ']): r_amount = normal_amount
                prefix = re.sub(rf'\s?{normal_amount}$', '', line).strip()
            else:
                prefix = line

        # 2. Cell Counting Logic
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        is_r = any(x in line for x in ['r', 'အာ'])
        line_cells = 0

        # --- Keywords Logic အုပ်စုများ ---
        if any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ပတ်ပူးပို', 'ပါပူး', 'ပူးပို', 'ပတ်ပူးပါ', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_cells = len(num_str) * 20
        elif any(x in line for x in ['ထိပ်စီး', 'ထိပ်', 'top', 't ', 'အပိတ်', 'ပိတ်', 'နောက်', 'န', 'bk', 'ဘရိတ်']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'ပူး', 'အပူး', 'puu', 'ပုး', 'အပူးစုံ', 'အပူးအစုံ']):
            line_cells = 10
        elif any(x in line for x in ['စပူး', 'စုံပူး', 'မပူး']):
            line_cells = 5
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_cells = 25 * (2 if is_r and any(x in line for x in ['စုံမ', 'မစုံ', 'စမ', 'မစ']) else 1)
        elif any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_cells = 50
        elif any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူးပါ', 'ပူး']):
            line_cells = len(num_str) ** 2
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(num_str)
            line_cells = n * (n - 1) if n > 1 else 0
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_cells = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_cells *= 2
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for digit in two_digits:
                    if is_r:
                        line_cells += 1 if digit[0] == digit[1] else 2
                    else:
                        line_cells += 1
            else:
                line_cells = len(num_str)

        # 3. Summation
        if normal_amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            if is_r and r_amount > 0 and r_amount != normal_amount:
                grand_total += (total_at_line * r_amount)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
