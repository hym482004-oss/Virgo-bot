import re

def calculate_2d(text):
    # Separators များကို space ပြောင်း၍ ရှင်းလင်းခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Amount Detection (R/အာ Logic အုပ်စု)
        r_amount = 0
        normal_amount = 0
        # R အုပ်စု: အာ, R, r, Rr
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

        # 2. Cell Counting (အုပ်စုအလိုက် တွက်ချက်ခြင်း)
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        is_r = any(x in line for x in ['r', 'အာ'])
        line_cells = 0

        # --- Keywords Logic ---
        
        # ၁။ ပတ်သီးအုပ်စု (n x 19)
        if any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_cells = len(num_str) * 19
            
        # ၂။ ပတ်ပူးအုပ်စု (n x 20)
        elif any(x in line for x in ['ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            line_cells = len(num_str) * 20
            
        # ၃။ ထိပ်/ပိတ်/ဘရိတ်အုပ်စု (n x 10)
        elif any(x in line for x in ['ထိပ်စီး', 'ထိပ်', 'top', 't ', 'အပိတ်', 'ပိတ်', 'နောက်', 'န', 'bk', 'ဘရိတ်']):
            line_cells = len(num_str) * 10
            
        # ၄။ ဆယ်ပြည့်/အပူး (Fixed 10)
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'ပူး', 'အပူး', 'puu', 'ပုး', 'အပူးစုံ', 'အပူးအစုံ', 'အပူးအကုန်']):
            line_cells = 10
            
        # ၅။ စပူး/မပူး (Fixed 5)
        elif any(x in line for x in ['စပူး', 'စုံပူး', 'မပူး']):
            line_cells = 5
            
        # ၆။ စုံစုံ/မမ/စုံမ (Fixed 25 သို့မဟုတ် R ပါက 50)
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'စူံစူံ', 'စူံစုံ', 'စုံစူံ']):
            line_cells = 25 * (2 if is_r and any(x in line for x in ['စုံမ', 'မစုံ', 'စမ', 'မစ']) else 1)
            
        # ၇။ စုံဘရိတ်/မဘရိတ် (Fixed 50)
        elif any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_cells = 50
            
        # ၈။ ခွေပူး (n x n)
        elif any(x in line for x in ['အပူးပါခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခွေပူး', 'အခွေပူး', 'ခပ']):
            line_cells = len(num_str) ** 2
            
        # ၉။ ခွေ (n x (n-1))
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(num_str)
            line_cells = n * (n - 1)
            
        # ၁၀။ ကပ် (Group 1 x Group 2)
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_cells = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_cells *= 2
        
        # ၁၁။ ဒဲ့ / R (အပူးပါလျှင် R အတွက် ၁ ကွက်သာယူသည်)
        else:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for digit in two_digits:
                    if is_r:
                        line_cells += 1 if digit[0] == digit[1] else 2
                    else:
                        line_cells += 1
            else:
                # ဂဏန်း ၁ လုံးတည်းဖြစ်လျှင် ၁ ကွက်ဟု ယူဆသည်
                line_cells = len(num_str)

        # 3. Final Calculation (အကွက်ရေ x Amount)
        if normal_amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            # ဒဲ့/အာ ဈေးမတူသော logic
            if is_r and r_amount > 0 and r_amount != normal_amount:
                grand_total += (total_at_line * r_amount)
            
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
