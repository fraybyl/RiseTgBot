from fluent.runtime import FluentLocalization
from loader import get_fluent_localization
bonus = 1

locale = get_fluent_localization()

print(f"Bonus value before formatting: {bonus}")
caption = locale.format_value('product-info', {
    'category': "хуй",
    'quantity': 50,
    'bonus': bonus if bonus is not None else None
})
print(f"Formatted caption: {caption}")