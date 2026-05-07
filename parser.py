import re

def get_market_rate(text):
    t = text.lower()
    # Market keywords and rates
    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'me', 'mega']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်ဆီ', 'မက်စီ', 'စီစီ']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'loa', 'loadon', 'laodon', 'လာလာ', 'လာအို']): return 0.07, "7%"
    if any(x in t for x in ['london', 'လန်လန်', 'လန်ဒန်', 'ld']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'ဂလို', 'glo']): return 0.03, "3%"
    
    return None, None # Market နာမည် ရှာမတွေ့ရင်

def calculate_bets(text):
    lines = text.split('\n')
    total_amount = 0
    valid_bet_found = False
    
    for line in lines:
        line = line.strip().lower()
        if not line or any(x in line for x in ['2d', 'total']): continue

        # Amount ရှာခြင်း (Line အဆုံးက ဂဏန်း)
        amt_match = re.search(r'(\d+)$', line)
        if not amt_match: continue
        final_amt = int(amt_match.group(1))

        # --- တွက်နည်းများ (အကျဉ်းချုပ်) ---
        # ဒဲ့ နှင့် R (12R500 သို့မဟုတ် 12 500 R250)
        numbers = re.findall(r'\d{2}', line)
        if numbers:
            r_amt_match = re.search(r'r(\d+)', line)
            d_amt_match = re.search(r'(\d+)r', line)
            d_amt = int(d_amt_match.group(1)) if d_amt_match else final_amt
            total_amount += len(numbers) * d_amt
            if r_amt_match:
                total_amount += len(numbers) * int(r_amt_match.group(1))
            elif 'r' in line:
                total_amount += len(numbers) * d_amt
            valid_bet_found = True
            continue

        # Keywords တွက်နည်းများ (ပတ်၊ ခွေ၊ ဘရိတ်...) - အပေါ်က logic အတိုင်း ဆက်သွားမယ်
        # ... (Parser logic full version)
        
    return total_amount if valid_bet_found else 0
