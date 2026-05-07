import re


def normalize_text(text):
    text = text.lower()

    # separator normalize
    for s in ["*", "-", "/", "'", "="]:
        text = text.replace(s, " ")

    return text


def get_last_amount(lines, index):
    """
    amount မပါတဲ့ line ကို
    အောက်က line amount inherit လုပ်
    """
    for i in range(index + 1, len(lines)):
        m = re.search(r'(\d+)$', lines[i])
        if m:
            return int(m.group(1))
    return 0


def extract_amount(line):
    """
    3 type
    500
    R500
    500R250
    """

    # split price
    split_match = re.search(r'(\d+)\s*r\s*(\d+)', line)
    if split_match:
        return int(split_match.group(1)), int(split_match.group(2)), "split"

    # only r
    r_match = re.search(r'r\s*(\d+)', line)
    if r_match:
        return int(r_match.group(1)), None, "r"

    # normal
    normal_match = re.search(r'(\d+)$', line)
    if normal_match:
        return int(normal_match.group(1)), None, "normal"

    return 0, None, None


def count_direct_numbers(line):
    return len(re.findall(r'\b\d{2}\b', line))


def calculate_bets(text):

    text = normalize_text(text)
    lines = [x.strip() for x in text.split("\n") if x.strip()]

    total = 0

    for idx, line in enumerate(lines):

        amount, r_amount, mode = extract_amount(line)

        if amount == 0:
            amount = get_last_amount(lines, idx)

        if amount == 0:
            continue

        # remove amount from line
        pure_line = re.sub(r'\d+\s*r\s*\d+$', '', line)
        pure_line = re.sub(r'r\s*\d+$', '', pure_line)
        pure_line = re.sub(r'\d+$', '', pure_line)

        # number list
        nums = re.findall(r'\d+', pure_line)

        # ==========================
        # GROUP 1 (10 BLOCK)
        # ==========================
        group_10 = [
            'ဆယ်ပြည့်', 'ဆယ်ပြည်', 'ဆယ့်ပြည်',
            'အပူး', 'ပူး',
            'ထိပ်', 'ထ', 'top', 't',
            'ပိတ်', 'အပိတ်', 'နောက်', 'အနောက်',
            'ဘရိတ်', 'bk',
            'ပါဝါ', 'ပဝ', 'pw', 'power',
            'နက္ခတ်', 'nk', 'နက', 'နခ'
        ]

        if any(k in pure_line for k in group_10):
            total += 10 * amount
            continue

        # ==========================
        # GROUP 2 (R)
        # ==========================
        if mode == "r":
            direct_count = count_direct_numbers(pure_line)
            if direct_count > 0:
                total += (direct_count * amount * 2)
                continue

        # ==========================
        # GROUP 3 (Direct)
        # ==========================
        direct_count = count_direct_numbers(pure_line)
        if direct_count > 0 and mode == "normal":
            total += direct_count * amount
            continue

        # ==========================
        # GROUP 4 (PAT 19)
        # ==========================
        if any(k in pure_line for k in ['ပတ်', 'အပါ', 'ပါ', 'ch', 'p']):
            total += 19 * amount
            continue

        # ==========================
        # GROUP 5 (KHWE)
        # ==========================
        if any(k in pure_line for k in ['ခွေ', 'အခွေ', 'ခ']):
            n = len(nums)
            total += (n * (n - 1)) * amount
            continue

        # ==========================
        # GROUP 6 (KHWE PU)
        # ==========================
        if any(k in pure_line for k in ['ခွေပူး', 'အခွေပူး']):
            n = len(nums)
            total += (n * n) * amount
            continue

        # ==========================
        # GROUP 7 (5 BLOCK)
        # ==========================
        if any(k in pure_line for k in ['စပူး', 'စုံပူး', 'မပူး']):
            total += 5 * amount
            continue

        # ==========================
        # GROUP 8 (25 BLOCK)
        # ==========================
        if any(k in pure_line for k in [
            'စစ', 'မမ', 'စမ', 'မစ',
            'စုံစုံ', 'စုံမ', 'စူံစူံ'
        ]):
            if mode == "r":
                total += 50 * amount
            else:
                total += 25 * amount
            continue

        # ==========================
        # GROUP 9 (KAP)
        # ==========================
        if any(k in pure_line for k in ['ကပ်', 'အကပ်', 'ကို']):
            if len(nums) >= 2:
                a = len(nums[0])
                b = len(nums[1])

                if mode == "r":
                    total += a * b * amount * 2
                else:
                    total += a * b * amount
            continue

        # ==========================
        # GROUP 10 (50 BLOCK)
        # ==========================
        if any(k in pure_line for k in [
            'စုံဘရိတ်', 'စုံbk',
            'မbk', 'မဘရိတ်',
            'စဘရိတ်'
        ]):
            total += 50 * amount
            continue

        # ==========================
        # GROUP 11 (20 BLOCK)
        # ==========================
        if any(k in pure_line for k in [
            'ပတ်ပူး',
            'ပူးပို',
            'ပတ်ပူးပို',
            'ထန',
            'ထပ',
            'ထိပ်ပိတ်',
            'ထိပ်နောက်',
            'ညီကို',
            'ညီအကို',
            'ညီအစ်ကို'
        ]):
            total += 20 * amount
            continue

        # ==========================
        # SPLIT PRICE
        # 23 45 56=500R250
        # ==========================
        if mode == "split":
            count = count_direct_numbers(pure_line)
            total += (count * amount) + (count * r_amount)
            continue

    return total
