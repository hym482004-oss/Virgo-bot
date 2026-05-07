import re

# ================= MARKET RATE =================
def get_market_rate(text):
    t = text.lower()

    if any(x in t for x in ['dubai', 'ဒူ', 'du']):
        return 0.07, "7%"
    if any(x in t for x in ['mega', 'me', 'မီ', 'mega']):
        return 0.07, "7%"
    if any(x in t for x in ['max', 'maxi', 'မက်']):
        return 0.07, "7%"
    if any(x in t for x in ['lao', 'ld', 'london']):
        return 0.07, "7%"
    if any(x in t for x in ['mm']):
        return 0.10, "10%"
    if any(x in t for x in ['global', 'glo']):
        return 0.03, "3%"

    return 0.07, None


# ================= CLEAN =================
def normalize(text):
    return text.lower()


def extract_amount(line):
    m = re.search(r'r(\d+)', line)
    if m:
        return int(m.group(1)), True  # R amount

    m = re.search(r'(\d+)$', line)
    if m:
        return int(m.group(1)), False

    return 0, False


# ================= CORE ENGINE =================
def calculate_bets(text):

    text = normalize(text)

    text = text.replace('*', ' ').replace('/', ' ').replace('.', ' ').replace('=', ' ').replace('-', ' ')
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    total = 0
    found = False

    for line in lines:

        amt, is_r = extract_amount(line)
        if amt == 0:
            continue

        # ================= KHWE =================
        if any(x in line for x in ['ခွေပူး', 'ခပ', 'အခွေပူး']):
            nums = re.findall(r'\d+', line)
            n = len(nums)
            count = n * n
            total += count * amt
            found = True
            continue

        if any(x in line for x in ['ခွေ', 'ခ', 'အခွေ']):
            nums = re.findall(r'\d+', line)
            n = len(nums)
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
        if any(x in line for x in ['ထိပ်', 'ထ', 'top', 't']):
            total += 10 * amt
            found = True
            continue

        # ================= BRAKE =================
        if any(x in line for x in ['ဘရိတ်', 'bk']):
            total += 10 * amt
            found = True
            continue

        if any(x in line for x in ['စုံဘရိတ်', 'စဘရိတ်']):
            total += 50 * amt
            found = True
            continue

        # ================= POWER / NK =================
        if any(x in line for x in ['ပါဝါ', 'pw', 'ပဝ']):
            total += 10 * amt
            found = True
            continue

        if any(x in line for x in ['နက္ခတ်', 'nk']):
            total += 10 * amt
            found = True
            continue

        # ================= BRO =================
        if any(x in line for x in ['ညီကို', 'ညီအကို', 'ညီအစ်ကို']):
            total += 20 * amt
            found = True
            continue

        # ================= SET (25) =================
        if any(x in line for x in ['စစ', 'မမ', 'စမ', 'မစ', 'စုံစုံ']):
            mult = 2 if is_r else 1
            total += 25 * amt * mult
            found = True
            continue

        # ================= SINGLE NUMBERS (fallback) =================
        nums = re.findall(r'\d{2}', line)

        if nums:
            if is_r:
                total += len(nums) * amt * 2
            else:
                total += len(nums) * amt

            found = True

    return total if found else 0
