import re

def get_market_rate(text):
    t = text.lower()
    if any(x in t for x in ['dubai', 'ဒူ', 'du', 'mega', 'me', 'မီ', 'max', 'maxi', 'မက်', 'lao', 'ld', 'london']):
        return 0.07, "7%"
    if 'mm' in t: return 0.10, "10%"
    if 'glo' in t: return 0.03, "3%"
    return 0.07, "7%"

def calculate_bets(text):
    # စာကြောင်းရှည်ကြီးတွေကို အပိုင်းပိုင်းခွဲရလွယ်အောင် clean လုပ်မယ်
    text = text.replace('=', ' ').replace('-', ' ').replace(',', ' ').replace('။', ' ')
    lines = [l.strip() for l in text.lower().split('\n') if l.strip()]
    
    grand_total = 0
    pending_units = 0 

    for line in lines:
        if any(x in line for x in ['total', 'cash', '2d', 'ဘဲလွဲ', 'ကံကောင်း']): continue
        
        # 1. Amount ကို အရင်ဆုံး ရှာထုတ်မယ်
        amt_match = re.search(r'(?:r|R| )?(\d{3,10})$', line)
        amt = int(amt_match.group(1)) if amt_match else 0
        prefix = line.replace(amt_match.group(0), "").strip() if amt_match else line
        
        if not prefix and amt > 0: # Amount ပဲပါတဲ့စာကြောင်းဆိုရင်
            grand_total += pending_units * amt
            pending_units = 0
            continue

        line_unit = 0
        is_r = any(x in line for x in ['r', 'အာ', 'ာ'])
        num_blocks = re.findall(r'\d+', prefix)
        all_digits = "".join(num_blocks)
        
        # 2. Keyword တစ်ခုထက်ပိုပါရင် အကုန်ပေါင်းတွက်မည့် Logic
        
        # [Group 11] 50 Blocks
        if any(x in prefix for x in ['စုံဘရိတ်', 'မဘရိတ်', 'စဘရိတ်', 'စုံbk', 'မbk']):
            line_unit += 50
        
        # [Group 9] 25 Blocks
        if any(x in prefix for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ']):
            line_unit += 25

        # [Group 1] 20 Blocks
        if any(x in prefix for x in ['ညီကို', 'ညီအကို', 'ပတ်ပူး', 'ပူးပို', 'ထန', 'ထပ', 'ထိပ်ပိတ်']):
            line_unit += 20

        # [Group 5] 19 Blocks (ဂဏန်းအလုံးရေအလိုက် မြှောက်မယ်)
        if any(x in prefix for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']) and 'ပတ်ပူး' not in prefix:
            line_unit += len(all_digits) * 19

        # [Group 2] 10 Blocks (Keyword အစုံပါရင် အကုန်ပေါင်းမယ်)
        kw_10 = ['ပါဝါ', 'ပဝ', 'pw', 'နက္ခတ်', 'nk', 'နက', 'နခ', 'ဘရိတ်', 'bk', 'ထိပ်', 'ပိတ်', 'အပူး', 'ဆယ်ပြည့်']
        for kw in kw_10:
            if kw in prefix:
                multiplier = len(num_blocks) if num_blocks else 1
                line_unit += multiplier * 10

        # [Group 6, 7] ခွေ / ခွေပူး
        if any(x in prefix for x in ['ခွေပူး', 'အခွေပူး', 'အပူးပါ', 'ခပ']):
            n = len(all_digits)
            line_unit += n * n
        elif any(x in prefix for x in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(all_digits)
            line_unit += n * (n - 1)

        # [Group 10] ကပ်/ကို
        if any(x in prefix for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(num_blocks) >= 2:
                line_unit += len(num_blocks[0]) * len(num_blocks[1])
                if is_r: line_unit *= 2

        # [Group 3, 4] ဒဲ့ / R
        # Keyword တခြားဟာတွေ မပါမှ ဒဲ့/R တွက်မယ်
        if line_unit == 0:
            two_digits = re.findall(r'\d{2}', prefix)
            if two_digits:
                line_unit += len(two_digits) * (2 if is_r else 1)
            else:
                line_unit += len(all_digits) * (2 if is_r else 1)

        # 3. Final Calculation
        if amt > 0:
            grand_total += (pending_units + line_unit) * amt
            pending_units = 0
        else:
            pending_units += line_unit

    return grand_total, []
