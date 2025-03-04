# this program is for updating multiple grades at a same time
# and automatically combine files into one
# so no need to update one by one

import json
from count_data import count
from main import update
from traceback import print_exc

old_file = input("Enter old file to be updated: ")
with open(old_file, "r") as f:
    old = json.load(f)
data = old["data"]
formed_list = {}
# form list into key value pair in able to find old data quick
for i in data:
    formed_list.update({str(i["id"]): i})
data = formed_list


# fuck my naming skill
grades = []
grades_name = {}
result = []
save_to = input("Enter output file name: ")
try:
    grades_cnt = int(input("Enter number of grades: "))
    for i in range(grades_cnt):
        print(f"Enter grade {i + 1}: ")
        grade = input("Grade name: ")
        id = input("Grade id: (first 2 digits of id) ")
        grade_info = {
            "id": id,
            "min_id": input("Min id (after 2 digits): "),
            "max_id": input("Max id (after 2 digits): "),
            "min_year": int(input("Min year for guessing birthday: ")),
            "max_year": int(input("Max year for guessing birthday: ")),
        }
        grades.append(grade_info)
        grades_name.update({id: grade})

    for grade in grades:
        grade_data = update(
            grade["id"],
            grade["id"],
            grade["min_id"],
            grade["max_id"],
            grade["min_year"],
            grade["max_year"],
            data,
        )
        result.extend(grade_data)
except KeyboardInterrupt:
    print("KeyboardInterrupt")
except Exception as e:
    print_exc()

with open(save_to, "w") as f:
    json.dump(count(result, grades_name), f)
