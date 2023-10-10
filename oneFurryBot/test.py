from decimal import Decimal
y = Decimal(1.345).quantize(Decimal("0.01"), rounding="ROUND_HALF_UP")
print(float(y) + 1.2)
