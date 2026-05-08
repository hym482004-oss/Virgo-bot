import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # separators အစုံကို space ပြောင်းမယ်
    clean_text = re.sub(r'[/\-=*.,:]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 # Amount မပါသေးတဲ့ အကွက်တွေကို စုထားဖို့
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm']): continue
        
        # 1. Amount Detection
        r_amount = 0
        normal_amount = 0
        
        r_match = re.search(r'r\s?(\d+)', line)
        if r_match:
            r_amount = int(r_match.group(1))
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
        else:
            nums = re.findall(r'\d+', line)
            if nums:
                normal_amount = int(nums[-1])
                if any(x in line for x in ['r', 'အာ', 'ာ']):
                    r_amount = normal_amount

        # 2. Extract Numbers & Keywords for counting
        # Amount ကို ဖယ်လိုက်မယ်
        prefix = line.replace(str(normal_amount), "").replace(str(r_amount), "").replace('r', '')
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        
        line_cells = 0

        # --- Keyword Groups ---
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            line_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            line_cells = 25 * (2 if is_r else 1)
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ထိပ်ပိတ်', 'ထိပ်နောက်', 'ထိပ်အပိတ်']):
            line_cells = 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'by', 'ch', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'အပူး', 'အပူးစုံ', 'ပါဝါ', 'pw', 'power', 'နက္ခတ်', 'nk']):
            line_cells = 10
        elif any(x in line for x in ['ထိပ်', 'ထ ', 'top', 't ', 'ပိတ်', 'အပိတ်', 'နောက်', 'ဘရိတ်', 'bk']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['စုံပူး', 'မပူး', 'စပူး']):
            line_cells = 5
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_cells = len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_cells *= 2
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ', 'ပူး']):
            n = len(num_str)
            line_cells = n * n
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ ']):
            n = len(num_str)
            line_cells = n * (n - 1)
        else:
            # Direct/R (2 digits pairs)
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_cells = len(two_digits)
            elif num_str:
                line_cells = len(num_str) # Single digits mixed

        # 3. Process Calculation
        if normal_amount > 10: # Amount လို့ ယူဆရတဲ့ ဂဏန်းဖြစ်မှ တွက်မယ်
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            # R amount သီးသန့်ရှိရင် ထပ်ပေါင်းမယ်
            if is_r and r_amount > 0 and r_amount != normal_amount:
                grand_total += (total_at_line * r_amount)
            
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
