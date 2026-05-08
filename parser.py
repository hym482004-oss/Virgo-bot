import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # Separators များကို ရှင်းလင်းခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Amount Detection
        r_amount = 0
        normal_amount = 0
        r_match = re.search(r'r\s?(\d+)$', line)
        
        if r_match:
            r_amount = int(r_match.group(1))
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
            prefix = line_pre_r[:(norm_match.start() if norm_match else len(line_pre_r))].strip()
        else:
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_amount = int(all_nums[-1])
                if any(x in line for x in ['r', 'အာ', 'ာ']): r_amount = normal_amount
                prefix = re.sub(rf'\s?{normal_amount}$', '', line).strip()
            else:
                prefix = line

        # 2. Cell Counting Logic
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        line_cells = 0

        # --- Keyword Fixed Cells ---
        if any(x in line for x in ['အပူး', 'ပါဝါ', 'pw', 'နက္ခတ်', 'nk']):
            line_cells = 10 # Keyword နဲ့ရေးရင် R ပါလဲ ၁၀ ကွက်ပုံသေ
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို']):
            line_cells = 20
        elif any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            line_cells = 25 * (2 if is_r and any(x in line for x in ['စုံမ', 'မစုံ']) else 1)
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'by', 'ch', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ထိပ်', 'ထ ', 'top', 'ပိတ်', 'နောက်', 'ဘရိတ်', 'bk']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူးပါ', 'ပူး']):
            line_cells = len(num_str) ** 2
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ ']):
            n = len(num_str)
            line_cells = n * (n - 1)
        else:
            # --- ဒဲ့ဂဏန်းများတွင် အပူးပါလျှင် R အတွက် ၁ ကွက်သာတွက်ခြင်း ---
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for digit in two_digits:
                    if is_r:
                        # အပူးဖြစ်လျှင် ၁ ကွက်၊ မဟုတ်လျှင် ၂ ကွက် (R)
                        line_cells += 1 if digit[0] == digit[1] else 2
                    else:
                        line_cells += 1
            else:
                line_cells = len(num_str)

        # 3. Final Summation
        if normal_amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            # R amount ခွဲတွက်ချက်မှု (ဒဲ့/အာ ဈေးမတူလျှင်)
            if is_r and r_amount > 0 and r_amount != normal_amount:
                grand_total += (total_at_line * r_amount)
            
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
