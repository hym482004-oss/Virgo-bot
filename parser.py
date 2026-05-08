import re

def get_market_data(text):
    text = text.lower()
    if 'mm' in text: return 0.10, "10%"
    if any(x in text for x in ['glo', 'global', 'ဂလို']): return 0.03, "3%"
    return 0.07, "7%"

def calculate_2d(text):
    # Separators အားလုံးကို space ပြောင်းမယ်
    clean_text = re.sub(r'[/\-=*.,:;]', ' ', text.lower())
    lines = clean_text.split('\n')
    
    grand_total = 0
    pending_cells = 0
    
    for line in lines:
        line = line.strip()
        # Summary စာကြောင်းတွေကို ကျော်မယ်
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']): 
            continue

        # ==================================
        # STEP 1: KEYWORDS အရင်ရှာမယ်
        # ==================================
        rule_type = "direct"
        multiplier = 1
        is_r = any(x in line for x in ['r', 'အာ'])

        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            rule_type = "even_brake"
            base_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            rule_type = "sam"
            base_cells = 25
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန်', 'ထပ်', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            rule_type = "pat_pu"
            base_cells = 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            rule_type = "pat"
            base_cells = 19
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'အပူး', 'ပူး', 'အပူးစုံ', 'ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက်', 'နခ']):
            rule_type = "ten"
            base_cells = 10
        elif any(x in line for x in ['ထိပ်', 'ထ', 'top', 't', 'ပိတ်', 'အပိတ်', 'နောက်', 'အနောက်', 'ဘရိတ်', 'bk']):
            rule_type = "top_brake"
            base_cells = 10
        elif any(x in line for x in ['စုံပူး', 'မပူး', 'စပူး']):
            rule_type = "so_pu"
            base_cells = 5
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            rule_type = "kap"
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခပ်']):
            rule_type = "khwe_pu"
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            rule_type = "khwe"

        # ==================================
        # STEP 2: အကွက်ရေ တွက်မယ်
        # ==================================
        numbers_in_line = re.findall(r'\d+', line)
        line_cells = 0

        if rule_type == "kap":
            # ကပ် = a × b
            if len(numbers_in_line) >= 2:
                a = len(str(numbers_in_line[0]))
                b = len(str(numbers_in_line[1]))
                line_cells = a * b
        elif rule_type == "khwe_pu":
            # ခွေပူး = n × n
            all_digits = "".join(map(str, numbers_in_line))
            n = len(all_digits)
            line_cells = n * n
        elif rule_type == "khwe":
            # ခွေ = n × (n-1)
            all_digits = "".join(map(str, numbers_in_line))
            n = len(all_digits)
            line_cells = n * (n - 1)
        elif rule_type == "top_brake":
            # ထိပ်/ဘရိတ် = 10 × အရေအတွက်
            all_digits = "".join(map(str, numbers_in_line))
            n = len(all_digits)
            line_cells = base_cells * n
        else:
            # အခြားအမျိုးအစားတွေ
            line_cells = base_cells

        # R ပါရင် 2 နဲ့မြှောက်
        if is_r:
            line_cells = line_cells * 2

        # ==================================
        # STEP 3: AMOUNT ရှာမယ်
        # ==================================
        amount = 0
        # နောက်ဆုံးဂဏန်းကို ယူ
        if numbers_in_line:
            amount = int(numbers_in_line[-1])

        # ==================================
        # စုစုပေါင်းတွက်မယ်
        # ==================================
        if amount > 10: 
            total_at_line = (pending_cells + line_cells)
            grand_total += (total_at_line * amount)
            pending_cells = 0
        else:
            pending_cells += line_cells

    return grand_total
