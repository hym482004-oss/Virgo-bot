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
    
    for line in lines:
        line = line.strip()
        if not line or any(x in line for x in ['total', 'cash', 'ဘဲလွဲ', 'pm', 'စုစုပေါင်း', 'လက်ခံ', 't=', 't/']): 
            continue

        # ==================================
        # STEP 1: KEYWORDS ရှာပါ
        # ==================================
        base_cells = 0
        is_r = any(x in line for x in ['r', 'အာ'])
        
        # စာကြောင်းထဲက ဂဏန်းတွေကို ခွဲထုတ်
        numbers = re.findall(r'\d+', line)
        if not numbers:
            continue
            
        # Amount ကို နောက်ဆုံးက ယူ
        amount = int(numbers[-1])
        
        # ကျန်တဲ့ဂဏန်းတွေကို ယူ
        num_str = "".join(numbers[:-1])
        n = len(num_str)

        # --- Keywords စစ်ပါ ---
        if any(x in line for x in ['စုံဘရိတ်', 'စုံbk', 'မbk', 'မဘရိတ်', 'စဘရိတ်']):
            base_cells = 50
        elif any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ', 'စုံမ', 'မစုံ']):
            base_cells = 25
        elif any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို', 'ပတ်ပူး', 'ပူးပို', 'ပတ်ပူးပို', 'ထန်', 'ထပ်', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            base_cells = 20
        elif any(x in line for x in ['ပတ်သီး', 'အပါ', 'ပတ်', 'ပါ', 'ch', 'p']):
            base_cells = 19
        elif any(x in line for x in ['ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်', 'အပူး', 'ပူး', 'အပူးစုံ', 'ပါဝါ', 'ပဝ', 'pw', 'power', 'နက္ခတ်', 'nk', 'နက်', 'နခ']):
            base_cells = 10
        elif any(x in line for x in ['ထိပ်', 'top', 't', 'ပိတ်', 'အပိတ်', 'နောက်', 'အနောက်', 'ဘရိတ်', 'bk']):
            if num_str:
                base_cells = len(num_str) * 10
            else:
                base_cells = 10
        elif any(x in line for x in ['စုံပူး', 'မပူး', 'စပူး']):
            base_cells = 5
        elif any(x in line for x in ['ကပ်', 'အကပ်', 'ကို']):
            if len(numbers) >= 2:
                # ပထမဂဏန်းရှည် ၊ ဒုတိယဂဏန်းရှည်
                base_cells = len(str(numbers[0])) * len(str(numbers[1]))
        elif any(x in line for x in ['ခွေပူး', 'အပူးပါ', 'အပူးအပြီးပါ', 'ခပ်']):
            base_cells = n * n
        elif any(x in line for x in ['ခွေ', 'အခွေ', 'ခ']):
            base_cells = n * (n - 1)
        else:
            # ဒဲ့ / Direct
            base_cells = len(num_str) if num_str else 0

        # ==================================
        # STEP 2: အကွက်ရေ တွက်ပါ
        # ==================================
        total_cells = base_cells
        
        # R ပါရင် 2 နဲ့မြှောက်
        if is_r:
            total_cells = total_cells * 2

        # ==================================
        # STEP 3: အကွက်ရေနဲ့ Amount မြှောက်ပါ
        # ==================================
        grand_total += (total_cells * amount)

    return grand_total


def format_result(username, total_amount, discount_rate, discount_text):
    discount_amount = int(total_amount * discount_rate)
    final_amount = total_amount - discount_amount
    
    return f"""👤 {username}
--------------------
စုစုပေါင်း = {total_amount:,} ကျပ်
{discount_text} Cashback = {discount_amount:,} ကျပ်
--------------------
လက်ခံရမည့်ငွေ = {final_amount:,} ကျပ်
--------------------
ကံကောင်းပါစေ"""
