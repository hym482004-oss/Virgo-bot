import re

# ================= MARKET RATE =================
def get_market_rate(text):
    t = text.lower()

    if any(x in t for x in ['dubai', 'ဒူ', 'du']): return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ']): return 0.07, "7%"
    if any(x in t for x in ['maxi', 'max', 'မက်']): return 0.07, "7%"
    if any(x in t for x in ['lao', 'ld', 'london']): return 0.07, "7%"
    if any(x in t for x in ['mm']): return 0.10, "10%"
    if any(x in t for x in ['global', 'glo']): return 0.03, "3%"

    return 0.07, None


# ================= CLEAN =================
def extract_amount(line):
    # R case
    r_match = re.search(r'r(\d+)', line)
    if r_match:
        return int(r_match.group(1)), True

    # normal amount (last number)
    m = re.search(r'(\d+)$', line)
    if m:
        return int(m.group(1)), False

    return 0, False


# ================= MAIN ENGINE =================
def calculate_bets(text):

    text = text.lower()

    # normalize symbols
    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')

    lines = [l.strip() for l in text.split('\n') if l.strip()]

    total = 0
    found = False

    for line in lines:

        amt, is_r = extract_amount(line)
        if amt == 0:
            continue

        # ================= KHWE =================
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူး', 'ခွေ']):
            nums = re.findall(r'\d+', line)
            n = len(nums)

            if any(x in line for x in ['ခွေပူး', 'ခပ', 'အပူး']):
                count = n * n
            else:
                count = n * (n - 1)

            total += count * amt
            found = True
            continue

        # ================= PAT =================
        if any(x in line for x in ['ပတ်ပူး', 'ထန', 'ထပ', 'ထိပ်ပိတ်', 'ထိပ်နောက်']):
            total += 20 * amt
            found = True
            continue

        if any(x in line for x in ['ပတ်', 'ပါ', 'အပါ']):
            total += 19 * amt
            found = True
            continue

        # ================= TOP =================
        if any(x in line for x in ['ထိပ်', 'top', 't']):
            total += 10 * amt
            found = True
