import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # Symbol တွေအကုန် ရှင်းထုတ်မယ်
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'စုစုပေါင်း', 'လက်ခံ']):
            continue
        
        # ၁။ Amount Detection (ဒဲ့ဈေးရော R ဈေးရော ရှာမယ်)
        r_price = 0
        normal_price = 0
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        
        # R price ကို အရင်ရှာ (ဥပမာ R600)
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        if r_match:
            r_price = int(r_match.group(2))
            line_body = line[:r_match.start()].strip()
            # ဒဲ့ price ကို ထပ်ရှာ (ဥပမာ 500)
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

        # ၂။ အကွက်ရေ တွက်ခြင်း
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        line_cells = 0

        # Keywords အုပ်စုများ
        if any(x in line for x in ['ပတ်ပူးပို', 'ပါပူး', 'ပူးပို']):
            line_cells = len(num_str) * 20
        elif any(x in line for x in ['ပတ်သီး', 'ပတ်', 'ပါ']):
            line_cells = len(num_str) * 19
        elif any(x in line for x in ['ထိပ်', 'ပိတ်', 'bk']):
            line_cells = len(num_str) * 10
        elif any(x in line for x in ['ခွေ', 'ခ']):
            n = len(num_str)
            line_cells = n * (n - 1) if n > 1 else 0
        else:
            # ဒဲ့ဂဏန်းများအတွက် (R ပါရင် အပူးပါမကျန် ၂ ကွက်)
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for d in two_digits:
                    line_cells += 2 if is_r else 1
            else:
                line_cells = len(num_str) * (2 if is_r else 1)

        # ၃။ နောက်ဆုံး တွက်ချက်ခြင်း (Price ပေါင်း x အကွက်ရေ)
        total_price = normal_price + r_price
        
        if total_price > 10:
            grand_total += ((pending_cells + line_cells) * total_price)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
