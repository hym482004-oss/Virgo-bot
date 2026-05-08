import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # စာလုံးပေါင်းမှားနိုင်သော symbol များကို ရှင်းလင်းခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        # စာရင်းချုပ်စာသားများပါက ကျော်သွားရန်
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']):
            continue
        
        # 1. Amount & R Detection (ဒဲ့ဈေးရော R ဈေးရော ပေါင်းရန်)
        r_price = 0
        normal_price = 0
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        
        # R price ကို အရင်ရှာသည်
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        if r_match:
            r_price = int(r_match.group(2))
            line_pre_r = line[:r_match.start()].strip()
            # ဒဲ့ price ကို ထပ်ရှာသည်
            norm_match = re.search(r'(\d+)$', line_pre_r)
            normal_price = int(norm_match.group(1)) if norm_match else 0
            prefix = line_pre_r[:(norm_match.start() if norm_match else len(line_pre_r))].strip()
        else:
            # ဒဲ့ဈေး တစ်ခုတည်းပါလျှင်
            all_nums = re.findall(r'\d+', line)
            if all_nums
