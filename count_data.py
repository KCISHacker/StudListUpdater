import json
import time

file_count = int(input("Enter number of files: "))
data = []

for i in range(file_count):
    with open(input(f"Enter file name {i + 1}: "), "r") as f:
        data.extend(json.load(f))


# Get current time and convert to yyyy-MM-dd format
current_date = time.strftime("%Y-%m-%d")

result = {}
grade = {}
processed_data = []

for datum in data:
    if datum.get("id") is None:
        continue

    first_two_digits = str(datum.get("id"))[:2]

    if first_two_digits not in grade:
        grade_input = input(f"Enter grade for {first_two_digits}: ")
        grade.update({
            first_two_digits: grade_input
        })
        continue
    
    datum.update({
        "grade": grade.get(first_two_digits)
    })

    processed_data.append(datum)

result.update({
    "last_update": current_date,
    "count": len(data),
    "data": processed_data
})

with open(input("Enter output file name: "), "w") as f:
    json.dump(result, f)