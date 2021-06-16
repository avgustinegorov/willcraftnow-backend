from billing.models import Discount

def run(*args):

    try:
        for i in range(1, 47):
            discount_amount = 49
            is_active = True
            discount_code = f"DBS-WILLCRAFT-{i:03d}"
            print(discount_code)
            if not Discount.objects.filter(discount_code=discount_code).exists():
                discount = Discount.objects.create(
                    discount_amount=discount_amount,
                    discount_target='WILL_PRICE',
                    discount_type='PERCENTAGE',
                    is_active=True,
                    discount_code=discount_code,
                )
                print('Created', discount)
    except:
        pass
