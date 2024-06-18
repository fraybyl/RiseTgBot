# Исходные данные
data = [[], [('AUG | Contractor (Minimal Wear)', 1, 2.691), ('Dreams & Nightmares Case', 2, 87.906), ('Kilowatt Case', 3, 23.21), ('MP9 | Slide (Battle-Scarred)', 1, 2.691), ('Sticker | w0nderful (Champion) | Copenhagen 2024', 1, 2.691), ('Sticker | iM (Champion) | Copenhagen 2024', 1, 2.691), ('Sawed-Off | Snake Camo (Field-Tested)', 1, 8.073), ('MP7 | Army Recon (Field-Tested)', 1, 2.691), ('Nova | Predator (Battle-Scarred)', 1, 2.691)]]

total_elements = 0
sum_3rd_elements = 0
filtered_items = []

for sublist in data:
    for item in sublist:
        if isinstance(item, tuple):
            if len(item) >= 2:
                total_elements += item[1]
            if len(item) >= 3:
                sum_3rd_elements += item[2] * item[1]
            if len(item) >= 1 and "Case" in item[0]:
                filtered_items.append(item[2])

print("Элементы, содержащие 'Case' в первом значении кортежа:")
for item in filtered_items:
    print(item)

print("Общее количество элементов в кортежах:", total_elements)
print("Сумма всех третьих значений кортежей:", sum_3rd_elements)
