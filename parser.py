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
        if not line or any(x in line for x in ['total', 'cash', 'စုစုပေါင်း', 'လက်ခံ']):
            continue
        
        # ၁။ Amount (ဈေးနှုန်း) ကို အရင်ရှာပါ
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        all_nums = re.findall(r'\d+', line)
        if not all_nums: continue
        
        # စာကြောင်းရဲ့ နောက်ဆုံးဂဏန်းကို Amount ဟုယူသည်
        amount = int(all_nums[-1])
        # ရှေ့က ဂဏန်းများ သို့မဟုတ် Keywords များကို ယူသည်
        prefix = re.sub(rf'\s?{amount}$', '', line).strip()
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        
        line_cells = 0

        # ၂။ Keywords နှင့် အကွက်ရေ တွက်ခြင်း
        if any(x in line for x in ['ပတ်ပူးပို', 'ပါပူး', 'ပူးပို', 'ထိပ်ပိတ်']):
            line_cells = len(num_str) * 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ထိပ်', 'ပိတ်', 'bk', 'ဘရိတ်']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(num_str)
            line_cells = (n * (n - 1)) if n > 1 else 0
        elif any(x in line for x in ['စုံစုံ', 'မမ', 'စုံမ', 'မစုံ']):
            line_cells = 25
        else:
            # ဒဲ့ဂဏန်းများအတွက် (R ပါက ၂ ကွက်၊ မပါက ၁ ကွက်)
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_cells = len(two_digits) * (2 if is_r else 1)
            else:
                line_cells = len(num_str) * (2 if is_r else 1)

        # ၃။ အကွက်ရေ x Amount (နောက်ဆုံးအဆင့်)
        if amount > 10:
            grand_total += ((pending_cells + line_cells) * amount)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
