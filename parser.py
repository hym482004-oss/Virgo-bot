import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # Separators အားလုံးကို space ပြောင်းမယ်
    clean_text = re.sub(r'[/-=*.,:;]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0
    
    for line in lines:
        line = line.strip()
        # Summary စာကြောင်းတွေကို ကျော်မယ်
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']): continue
        
        r_amount = 0
        normal_amount = 0
        
        # --- 1. Amount ရှာခြင်း ---
        # R ပါတဲ့ပုံစံ (ဥပမာ r500, 500r250)
        r_match = re.search(r'r\s*(\d+)', line)
        if r_match:
            r_amount = int(r_match.group(1))
            # R ရှေ့က ဂဏန်းကို ယူ (ဥပမာ 500r250 ထဲက 500)
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)\s*$', line_pre_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
        else:
            # R မပါရင် နောက်ဆုံးဂဏန်းကို ယူ
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_amount = int(all_nums[-1])
                r_amount = normal_amount # R မပါရင် တူညီမယ်

        # --- 2. ပစ္စည်းအမျိုးအစား နှင့် ကွက်ရေ တွက်ခြင်း ---
        # Amount တွေဖြုတ်ပြီး ကျန်တဲ့နေရာကို ယူ
        prefix = line
        if r_amount > 0: prefix = re.sub(rf'r\s*{r_amount}', '', prefix).strip()
        if normal_amount > 0: prefix = re.sub(rf'{normal_amount}', '', prefix).strip()

        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        n = len(num_str)
        is_r = any(x in line for x in ['r', 'အာ'])
        
        line_cells = 0

        # --- KEYWORDS & FORMULA ---
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            # စုံဘရိတ် = 50 ကွက်
            line_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            # စမ/စစ = 25 ကွက်
            line_cells = 25
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန်', 'ထပ်', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            # ပတ်ပူး / ညီကို = 20 ကွက်
            line_cells = 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            # ပတ်သီး = 19 ကွက်
            line_cells = 19
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'အပူး', 'ပူး', 'အပူးစုံ', 'ပါဝါ', 'ပဝ', 'pw', 'နက္ခတ်', 'nk', 'နက်', 'နခ']):
            # ဆယ်ပြည့် / အပူး / ပါဝါ / နက္ခတ် = 10 ကွက်
            line_cells = 10
        elif any(x in line for x in ['ထိပ်', 'top', 't', 'ပိတ်', 'အပိတ်', 'နောက်', 'အနောက်', 'ဘရိတ်', 'bk']):
            # ထိပ် / ပိတ် / ဘရိတ် = 10 ကွက် × အရေအတွက်
            if num_str:
                line_cells = len(num_str) * 10
            else:
                line_cells = 10
        elif any(x in line for x in ['စုံပူး', 'မပူး', 'စပူး']):
            # စုံပူး = 5 ကွက်
            line_cells = 5
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            # ကပ် = a × b
            if len(num_blocks) >= 2:
                line_cells = len(num_blocks[0]) * len(num_blocks[1])
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခပ်']):
            # ခွေပူး = n × n
            line_cells = n * n
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            # ခွေ = n × (n-1)
            line_cells = n * (n - 1)
        else:
            # ဒဲ့ / Direct = ဂဏန်းရေအတိုင်း
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_cells = len(two_digits)
            elif num_str:
                line_cells = len(num_str)

        # --- 3. R ပါရင် နှစ်ခါတွက် ---
        if is_r:
            line_cells = line_cells * 2

        # --- 4. စုစုပေါင်းတွက်ချက်ခြင်း ---
        if normal_amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
