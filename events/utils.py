def add_paystack_charges(amount):
    """
    amount: int -> amount in Naira (not kobo)
    returns: amount in Kobo with Paystack fees added
    """
    paystack_percentage = 0.015  # 1.5%
    extra_fee = 100 if amount > 2500 else 0  # flat extra ₦100 if above ₦2500
    capped_fee = 2000  # max charge

    # Calculate Paystack fee
    fee = int((amount * paystack_percentage) + extra_fee + 20)
    if fee > capped_fee:
        fee = capped_fee

    gross_amount = amount + fee
    return gross_amount * 100  # convert to Kobo
