import re

def calculate_bets(text):
    # စာသားတစ်ခုလုံးမှာ 2d ပါမှ စတွက်မယ်
    if "2d" not in text.lower():
        return 0

    lines = text.split('\n')
    total_amount = 0
    has_error = False
    valid_bet_found = False
    
    for line in lines:
        line = line.strip().lower()
        # အပိုစာသားများကို ကျော်ရန်
        if not line or any(x in line for x in ['total', 'cash back', 'ကံကောင်းပါစေ', 'me 2d']):
            continue

        # 1. ဂဏန်းမပြည့်တာ စစ်ဆေးခြင်း (ဥပမာ - 6 တစ်လုံးတည်းဖြစ်နေရင်)
        # keywords မပါဘဲ ဂဏန်းတစ်လုံးတည်း (single digit) တွေ့ရင် error ပြမယ်
        if not any(k in line for k in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p', 'ထ', 'ထိပ်', 'ပိတ်', 'bk', 'ဘရိတ်', 'ခွေ', 'ခ', 'ကပ်', 'ကို', 'ပူး', 'ဆယ်', ' pw', 'nk']):
            single_digits = re.findall(r'\b\d{1}\b', line)
            if single_digits:
                has_error = True
                break

        # Amount ကို ရှာခြင်း (စာကြောင်းအဆုံးက ဂဏန်း)
        amt_match = re.search(r'(\d+)$', line)
        if not amt_match: continue
        final_amt = int(amt_match.group(1))

        # --- 2. ပတ်သီး / အပါ / Ch / P (၁၉ သို့မဟုတ် ၂၀ ကွက်) ---
        if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            is_patt_pu = any(x in line for x in ['ပူးပို', '၂၀ကွက်', '20ကွက်', 'ပတ်ပူး'])
            count = 20 if is_patt_pu else 19
            total_amount += len(nums[:-1] if len(nums) > 1 else [1]) * count * final_amt
            valid_bet_found = True
            continue

        # --- 3. ခွေ / အပူးပါခွေ (N*N-1 or N*N) ---
        if any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            nums = re.findall(r'\d', re.split(r'[ခခွေ]', line)[0])
            n = len(nums)
            if n > 1:
                if any(x in line for x in ['ပူး', 'အခွေပူး', 'ခပ']):
                    total_amount += (n * n * final_amt)
                else:
                    total_amount += (n * (n - 1) * final_amt)
                valid_bet_found = True
            continue

        # --- 4. ကပ် / ကို (N*N) ---
        if any(x in line for x in ['ကပ်', 'ကို', 'အကပ်']):
            nums_only = re.sub(r'[^0-9/]', ' ', line).strip()
            parts = [p for p in nums_only.split('/') if p]
            if len(parts) >= 2:
                count = len(parts[0]) * len(parts[1])
                total_amount += count * (2 if 'r' in line else 1) * final_amt
                valid_bet_found = True
            continue

        # --- 5. ၁၀ ကွက်တန် Keyword များ ---
        ten_keys = ['ထိပ်', 'ထ', 'top', 't', 'ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ပါဝါ', 'pw', 'နက္ခတ်', 'nk']
        if any(x in line for x in ten_keys):
            total_amount += 10 * final_amt
            valid_bet_found = True
            continue

        # --- 6. အထူးတွက်နည်းများ (ညီကို/စုံစုံ/စုံဘရိတ်) ---
        if any(x in line for x in ['ညီကို', 'ညီအကို']):
            total_amount += 20 * final_amt
            valid_bet_found = True
        elif any(x in line for x in ['စုံစုံ', 'စစ', 'မမ', 'စမ', 'မစ']):
            total_amount += (50 if 'r' in line else 25) * final_amt
            valid_bet_found = True
        elif 'ဘရိတ်' in line and any(x in line for x in ['စုံ', 'မ']):
            total_amount += 50 * final_amt
            valid_bet_found = True

        # --- 7. ဒဲ့ နှင့် R (12R500 သို့မဟုတ် 12 500 R250) ---
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            # R250 လိုမျိုး r နောက်က ဂဏန်းကို ရှာ
            r_amt_match = re.search(r'r(\d+)', line)
            # ဒဲ့ဈေး (R ရှေ့က ဂဏန်း သို့မဟုတ် final amount)
            d_amt_match = re.search(r'(\d+)r', line)
            
            d_amt = int(d_amt_match.group(1)) if d_amt_match else final_amt
            total_amount += len(numbers) * d_amt
            
            if r_amt_match:
                total_amount += len(numbers) * int(r_amt_match.group(1))
            elif 'r' in line and not r_amt_match:
                total_amount += len(numbers) * d_amt # 12R 500 ဆိုရင် ၂ ဆ
                
            valid_bet_found = True

    if has_error: return "error"
    return total_amount if valid_bet_found else 0
