import re

def calculate_bets(text):
    lines = text.split('\n')
    total_amount = 0
    has_error = False
    valid_bet_found = False
    
    for line in lines:
        line = line.strip().lower()
        if not line or 'total' in line: continue

        # ဂဏန်းအရေအတွက် စစ်ဆေးခြင်း (ဥပမာ - 6 တစ်လုံးတည်းဖြစ်နေရင်)
        # စာကြောင်းထဲမှာ 1 digit ပဲရှိတဲ့ ကိန်းဂဏန်းပါလား စစ်တာ (ပတ်သီး/ထိပ်/ပိတ် မဟုတ်လျှင်)
        if not any(keyword in line for keyword in ['ပတ်', 'ထိပ်', 'ပိတ်', 'bk', 'ဘရိတ်', 'ခွေ', 'ကပ်', 'ပူး']):
            single_digits = re.findall(r'\b\d{1}\b', line)
            if single_digits:
                has_error = True
                break

        # 1. ကပ်/R (e.g., 76/03 ကပ် R 100)
        if 'ကပ်' in line:
            match = re.search(r'([\d/]+).*?(\d+)$', line)
            if match:
                parts = match.group(1).split('/')
                amt = int(match.group(2))
                if len(parts) == 2:
                    total_amount += (len(parts[0]) * len(parts[1]) * (2 if 'r' in line else 1) * amt)
                    valid_bet_found = True
            continue

        # 2. ခွေပူး / ခပ
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'ပူးပါ']):
            match = re.search(r'(\d+).*?(\d+)$', line)
            if match:
                n = len(match.group(1))
                total_amount += (n * n * int(match.group(2)))
                valid_bet_found = True
            continue

        # 3. ခွေ (ရိုးရိုး)
        elif 'ခွေ' in line:
            match = re.search(r'(\d+).*?(\d+)$', line)
            if match:
                n = len(match.group(1))
                total_amount += (n * (n - 1) * int(match.group(2)))
                valid_bet_found = True
            continue

        # 4. ပတ်သီး / ဘရိတ် / အပူး / ထိပ် / ပိတ်
        if any(x in line for x in ['ပတ်', 'bk', 'ဘရိတ်', 'အပူး', 'ထိပ်', 'ပိတ်']):
            nums = re.findall(r'\d', line)
            amt_match = re.search(r'(\d+)$', line)
            if amt_match:
                amt = int(amt_match.group(1))
                if 'ပတ်' in line: total_amount += (len(nums[:-1]) * 19 * amt)
                else: total_amount += (10 * amt) # ဘရိတ်/ထိပ်/ပိတ်/အပူး
                valid_bet_found = True
            continue

        # 5. ဒဲ့ နှင့် R (e.g., 12 300 r200)
        numbers = re.findall(r'\b\d{2}\b', line)
        if numbers:
            r_amt_match = re.search(r'r\s*(\d+)', line)
            main_amt_match = re.search(r'(\d+)\s*(?:r|$)', line)
            if main_amt_match:
                amt = int(main_amt_match.group(1))
                total_amount += (len(numbers) * amt)
                if r_amt_match:
                    total_amount += (len(numbers) * int(r_amt_match.group(1)))
                valid_bet_found = True

    if has_error: return "error"
    return total_amount if valid_bet_found else 0
