import re

def get_market_data(text):
    """ဈေးကွက်အလိုက် ကော်မရှင်နှုန်းသတ်မှတ်ခြင်း"""
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    # ဒူဘိုင်း သို့မဟုတ် တခြားဈေးကွက်များအတွက် 7% Default
    return 0.07, "7%"

def calculate_2d(text):
    # စာလုံးပေါင်းမှားနိုင်သော symbol များကို space ဖြင့် အစားထိုးသည်
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 # Amount မပါသေးသော အကွက်များကို စုဆောင်းရန်
    
    for line in lines:
        line = line.strip()
        # အသုံးမလိုသော စာကြောင်းများကို ကျော်ရန်
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Amount Detection (ညာဘက်မှ ဘယ်ဘက်သို့ ရှာဖွေခြင်း)
        r_amount = 0
        normal_amount = 0
        
        # R amount ရှိမရှိ အရင်စစ်မည် (ဥပမာ 500R250 သို့မဟုတ် R500)
        r_match = re.search(r'r\s?(\d+)$', line)
        if r_match:
            r_amount = int(r_match.group(1))
            line_pre_r = line[:r_match.start()].strip()
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_amount = int(norm_match.group(1)) if norm_match else r_amount
            # Amount များကို ဖယ်လိုက်ပြီး ကျန်သောစာသား (Prefix) ကို ယူသည်
            prefix = line_pre_r[:(norm_match.start() if norm_match else len(line_pre_r))].strip()
        else:
            # R မပါလျှင် အနောက်ဆုံးဂဏန်းကို Amount ယူမည်
            all_nums = re.findall(r'\d+', line)
            if all_nums:
                normal_amount = int(all_nums[-1])
                if any(x in line for x in ['r', 'အာ', 'ာ']):
                    r_amount = normal_amount
                # စာကြောင်းအဆုံးရှိ Amount ကိုသာ ဖြတ်ထုတ်သည်
                prefix = re.sub(rf'\s?{normal_amount}$', '', line).strip()
            else:
                prefix = line

        # 2. Cell Counting (အကွက်ရေတွက်ချက်ခြင်း)
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        line_cells = 0

        # --- Keyword logic ---
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
        elif any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူးပါ', 'ပူး']):
            line_cells = len(num_str) ** 2
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ ']):
            n = len(num_str)
            line_cells = n * (n - 1)
        else:
            # ဒဲ့ သို့မဟုတ် R အတွက် ၂ လုံးစီတွဲ၍ ရေတွက်ခြင်း
            two_digits = re.findall(r'\d{2}', prefix)
            line_cells = len(two_digits) if two_digits else len(num_str)

        # 3. Final Summation (မြှောက်ခြင်း)
        if normal_amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * normal_amount)
            # R logic: ဒဲ့အာ ခွဲတွက်ခြင်း
            if is_r and r_amount > 0 and r_amount != normal_amount:
                grand_total += (total_at_line * r_amount)
            elif is_r and r_amount == normal_amount:
                # ဒဲ့ရော အာရော တူညီသောနှုန်းဖြင့် ထပ်ပေါင်းခြင်း
                grand_total += (total_at_line * normal_amount)
            
            pending_cells = 0 # တွက်ပြီးလျှင် buffer ကို ရှင်းထုတ်သည်
        else:
            pending_cells += line_cells # Amount မပါသေးလျှင် အကွက်ရေကို စုထားသည်

    return grand_total
