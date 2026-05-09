import re

def get_market_data(text):
    text = text.lower()
    # MM Market (10%)
    if any(x in text for x in ['mm', 'Mm', 'MM']):
        return 0.10, "10%"
    # Global Market (3%)
    if any(x in text for x in ['glo', 'global', 'ဂလို']):
        return 0.03, "3%"
    # 7% Markets
    market_7pct = [
        'dubai', 'ဒူ', 'ဒူဘိုင်း', 'du', 'mega', 'me', 'မီ', 'မီဂါ',
        'maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ', 'london', 'လန်လန်', 
        'လန်ဒန်', 'ld', 'landon', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို', 'lao'
    ]
    if any(x in text for x in market_7pct):
        return 0.07, "7%"
    return 0.07, "7%"

def calculate_2d(text):
    # Symbol တွေအကုန်လုံးကို Space အဖြစ် ပြောင်းလဲခြင်း
    clean_text = re.sub(r'[/\-=*.,:;+]', ' ', text.lower())
    lines = clean_text.split('\n')
    grand_total = 0
    pending_cells = 0 
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'စုစုပေါင်း', 'လက်ခံ']):
            continue
        
        # 1. Price Detection (ဒဲ့ဈေး နှင့် R ဈေး)
        r_price = 0
        normal_price = 0
        is_r = any(x in line for x in ['r', 'rr', 'အာ'])
        
        # R price ကို ရှာသည် (ဥပမာ R250)
        r_match = re.search(r'(r|rr|အာ)\s?(\d+)$', line)
        if r_match:
            r_price = int(r_match.group(2))
            line_body = line[:r_match.start()].strip()
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

        # 2. Cell Counting Logic
        num_blocks = re.findall(r'\d+', prefix)
        num_str = "".join(num_blocks)
        line_cells = 0

        # အကွက် ၂၅/၅၀ အုပ်စု
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
            line_cells = 50 if is_r else 25
        # အကွက် ၂၀ အုပ်စု
        elif any(x in line for x in ['ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ပတ်အကွက်20', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်', 'ညီကို', 'ညီအစ်ကို']):
            line_cells = (len(num_str) * 20) if num_str else 20
        # အကွက် ၅၀ အုပ်စု
        elif any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မဘရိတ်', 'မbk', 'စဘရိတ်']):
            line_cells = 50
        # အကွက် ၁၉ အုပ်စု
        elif any(x in line for x in ['ပတ်သီး', 'ပတ်', 'ပါ', 'ch', 'p', 'အပါ']):
            line_cells = len(num_str) * 19
        # အကွက် ၁၀ အုပ်စု
        elif any(x in line for x in ['ထိပ်', 'ပိတ်', 'bk', 'ဘရိတ်', 'ပူး', 'အပူး', 'ဆယ်ပြည်', 'ပါဝါ', 'pw', 'နက္ခတ်', 'nk']):
            line_cells = (len(num_str) * 10) if num_str else 10
        # ခွေ/ကပ်
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ']):
            line_cells = len(num_str) ** 2
        elif any(x in line for x in ['ခွေ', 'ခ']):
            n = len(num_str)
            line_cells = n * (n - 1) if n > 1 else 0
        elif any(x in line for x in ['ကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                a, b = len(num_blocks[0]), len(num_blocks[1])
                line_cells = (a * b * 2) if is_r else (a * b)
        else:
            # ဒဲ့ဂဏန်းများ
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                for d in two_digits: line_cells += 2 if is_r else 1
            else:
                line_cells = len(num_str) * (2 if is_r else 1)

        # 3. Final Calculation
        if normal_price > 10 or r_price > 10:
            # 23 45 56=500R250 logic
            # အကွက်အရေအတွက်ကို ဒဲ့ဈေးရော R ဈေးရောနဲ့ ခွဲတွက်တာက ပိုတိကျပါတယ်
            if is_r and r_price > 0 and normal_price > 0:
                # ဒဲ့ဈေးအတွက် အကွက်အရေအတွက် (is_r ဖြစ်နေလို့ line_cells က ၂ ဆဖြစ်နေတာကို ပြန်ဝေရမယ်)
                actual_base_cells = line_cells / 2 if not any(k in line for k in ['ပတ်', 'ထိပ်', 'ခွေ']) else line_cells
                line_total = (actual_base_cells * normal_price) + (actual_base_cells * r_price)
            else:
                line_total = (pending_cells + line_cells) * (normal_price + r_price)
            
            grand_total += line_total
            pending_cells = 0
        else:
            pending_cells += line_cells

    return {'total': int(grand_total)}
