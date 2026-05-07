import re

def calculate_bets(text):
    if "2d" not in text.lower():
        return 0

    lines = text.split('\n')
    total_amount = 0
    has_error = False
    valid_bet_found = False
    
    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ['total', 'cash back', 'ကံကောင်းပါစေ', 'me 2d']):
            continue

        # Amount ရှာခြင်း (စာကြောင်းအဆုံးက ဂဏန်း)
        amt_match = re.search(r'(\d+)$', line)
        if not amt_match: continue
        final_amt = int(amt_match.group(1))

        # 1. ဂဏန်းမပြည့်တာ စစ်ဆေးခြင်း
        if not any(k in line for k in ['ပတ်', 'ပါ', 'ch', 'p', 'ထ', 'bk', 'ခွေ', 'ခ', 'ကပ်', 'ကို', 'ပူး', 'ဆယ်', 'pw', 'nk', 'ညီ', 'စုံ', 'မ']):
            single_digits = re.findall(r'\b\d{1}\b', line)
            if single_digits:
                has_error = True
                break

        # --- 2. ပတ်သီး / အပါ / Ch / P (၁၉ သို့မဟုတ် ၂၀ ကွက်) ---
        if any(x in line for x in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            nums = re.findall(r'\d', line.split('ပတ်')[0] if 'ပတ်' in line else line)
            is_patt_pu = any(x in line for x in ['ပူးပို', '၂၀ကွက်', '20ကွက်', 'ပတ်ပူး'])
            count = 20 if is_patt_pu else 19
            total_amount += len(nums[:-1] if len(nums) > 1 else [1]) * count * final_amt
            valid_bet_found = True
            continue

        # --- 3. ခွေ / ခွေပူး (N*N-1 or N*N) ---
        if any(x in line for x in ['ခွေ', 'ခ']):
            nums = re.findall(r'\d', re.split(r'[ခခွေ]', line)[0])
            n = len(nums)
            if n > 1:
                if any(x in line for x in ['ပူး', 'ခပ']):
                    total_amount += (n * n * final_amt)
                else:
                    total_amount += (n * (n - 1) * final_amt)
                valid_bet_found = True
            continue

        # --- 4. ကပ် / ကို (N*N) ---
        if any(x in line for x in ['ကပ်', 'ကို']):
            parts = re.findall(r'\d+', line)
            if len(parts) >= 2:
                total_amount += (len(parts[0]) * len(parts[1])) * (2 if 'r' in line else 1) * final_amt
                valid_bet_found = True
            continue

        # --- 5. အထူး Keywords များ (၁၀, ၂၀, ၂၅, ၅၀ ကွက်) ---
        if any(x in line for x in ['ထိပ်', 'ထ', 'top', 't', 'ဘရိတ်', 'bk', 'အပူး', 'ပူး', 'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ပါဝါ', 'pw', 'နက္ခတ်', 'nk']):
            total_amount += 10 * final_amt
            valid_bet_found = True
        elif any(x in line for x in ['ညီကို', 'ညီအကို']):
            total_amount += 20 * final_amt
            valid_bet_found = True
        elif any(x in line for x in ['စုံစုံ', 'စစ', 'မမ', 'စမ', 'မစ']):
            total_amount += (50 if 'r' in line else 25) * final_amt
            valid_bet_found = True
        elif any(x in line for x in ['စုံဘရိတ်', 'မဘရိတ်']):
            total_amount += 50 * final_amt
            valid_bet_found = True

        # --- 6. ဒဲ့ နှင့် R (ဈေးကွဲတာတွေပါ တွက်သည်) ---
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_val_match = re.search(r'r(\d+)', line)
            d_val_match = re.search(r'(\d+)r', line)
            
            d_amt = int(d_val_match.group(1)) if d_val_match else final_amt
            total_amount += len(numbers) * d_amt
            
            if r_val_match:
                total_amount += len(numbers) * int(r_val_match.group(1))
            elif 'r' in line:
                total_amount += len(numbers) * d_amt # R ဆိုရင် ဒဲ့ဈေးအတိုင်း တစ်ဆထပ်ပေါင်း
            valid_bet_found = True

    if has_error: return "error"
    return total_amount if valid_bet_found else 0
