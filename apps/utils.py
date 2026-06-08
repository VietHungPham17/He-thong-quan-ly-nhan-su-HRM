from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def format_vnd_amount(value):
    if value in (None, ''):
        return ''

    try:
        amount = Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return str(value)

    return f'{int(amount):,}'.replace(',', '.')
