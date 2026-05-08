import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # သင်္ကေတတွေကို မဖျက်ခင် အရင်သိမ်းထားမည်
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    total = 0
    found = False

    for i, line in enumerate(lines):
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ']): continue
        
        # Line ထဲက ဂဏန်းအားလုံးကို ထုတ်သည်
        nums = re.findall(r'\d+', line)
        if not nums: continue
        amt = int(nums[-1])
        
        # Amount ရဲ့ ရှေ့ကပ်လျက်မှာ ဘာရှိသလဲ ရှာသည် (Keyword သို့မဟုတ် သင်္ကေတ)
        # ဥပမာ - "45 - 500" ဆိုရင် "-" ကို ရှာမည်
        prefix_part = line.split(str(amt))[0].strip()
        
        line_count = 0
        is_matched = False
        
        # အပေါ်စာကြောင်းပါ Context ယူရန်
        context_text = lines[i-1] + " " + line if i > 0 else line

        # --- ၁။ Keywords များ အရင်စစ်မည် ---
        # ခွေပူး
        if any(x in prefix_part for x in ['ခွေပူး', 'အခွေပူး', 'ပူးပို', 'အပူးပါ']):
            match = re.search(r'(\d+)\s*(?:ခွေပူး|အခွေပူး|ပူးပို|အပူးပါ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * n
            is_matched = True
        # ခွေ
        elif any(x in prefix_part for x in ['ခွေ', 'ခ', 'အခွေ']):
            match = re.search(r'(\d+)\s*(?:ခွေ|ခ|အခွေ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * (n - 1)
            is_matched = True
        # ပတ်သီး
        elif any(x in prefix_part for x in ['ပတ်', 'ပါ', 'အပါ']):
            match = re.search(r'(\d+)\s*(?:ပတ်|ပါ|အပါ)', context_text)
            n = len(match.group(1)) if match else 0
            line_count = n * 19
            is_matched = True
        
        # --- ၂။ Keyword မပါရင် သင်္ကေတများကို "ဒဲ့" အဖြစ် စစ်မည် ---
        if not is_matched:
            # သင်္ကေတတွေဖြစ်တဲ့ - * / . ' " တွေကို "ဒဲ့" အနေနဲ့ သတ်မှတ်သည်
            if any(s in prefix_part for s in ['-', '*', '/', '.', "'", '"', '=', '။']):
                # သင်္ကေတရှေ့က ဂဏန်းတွေကို ဒဲ့အဖြစ် ယူသည် (ဥပမာ "45 - 500")
                target_nums = re.findall(r'\d+', prefix_part)
                if target_nums:
                    is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                    # ၂ လုံးတွဲဂဏန်း ဖြစ်/မဖြစ် စစ်သည်
                    for n_str in target_nums:
                        if len(n_str) == 2:
                            line_count += (2 if is_r else 1)
                    is_matched = True

        # --- ၃။ အခြား Keywords (၁၀၊ ၂၀၊ ၅၀ ကွက်တန်) ---
        if not is_matched:
            unit = 0
            if any(x in prefix_part for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']): unit = 20
            elif any(x in prefix_part for x in ['ပါဝါ', 'pw', 'power', 'bk', 'ဘရိတ်']): unit = 10
            
            if unit > 0:
                match = re.search(r'(\d+)\s*(?:ညီကို|ပါဝါ|bk|pw|power|ဘရိတ်)', context_text)
                multiplier = len(match.group(1)) if match else 1
                line_count = unit * multiplier
                is_matched = True

        # --- ၄။ ဘာမှမပါရင် Default (၂ လုံးတွဲ ဒဲ့) ---
        if not is_matched:
            two_digits = re.findall(r'(?<!\d)\d{2}(?!\d)', prefix_part)
            if two_digits:
                is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
                line_count = len(two_digits) * (2 if is_r else 1)
                is_matched = True

        if is_matched or line_count > 0:
            total += line_count * amt
            found = True

    return total if found else 0
