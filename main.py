import json
from types import NoneType

from requests.adapters import HTTPAdapter
from urllib3 import Retry

import kcisinfo
import pypinyin

print("StudListUpdater Python by @KCISHacker")
mode = input("Enter mode (generate: g, update: u, query: q, name only: n): ")

if mode == "g":
    print("Generate mode")

    result_list = []
    query_grade_min = input("Enter min grade range: ")
    query_grade_max = input("Enter max grade range: ")
    query_range_min = input("Enter min range: ")
    query_range_max = input("Enter max range: ")
    guess_min_year = int(input("Enter min year for guessing birthday: "))
    guess_max_year = int(input("Enter max year for guessing birthday: "))

    print("\n")

    try:
        for i in range(int(query_grade_min), int(query_grade_max) + 1):
            for j in range(int(query_range_min), int(query_range_max) + 1):
                query_id = f"{i}{j:03}"
                result = kcisinfo.get_student_info(query_id, guess_min_year, guess_max_year)
                if result is not None:
                    result_list.append(result)
    except:
        print("An error occurred")

    print()
    save = input("Save result to: ")
    with open(save, "w") as f:
        json.dump(result_list, f, indent=4)
        print("Result saved to " + save)
elif mode == "u":
    print("Update mode")

    query_grade_min = input("Enter min grade range: ")
    query_grade_max = input("Enter max grade range: ")
    query_range_min = input("Enter min range: ")
    query_range_max = input("Enter max range: ")
    guess_min_year = int(input("Enter min year for guessing birthday: "))
    guess_max_year = int(input("Enter max year for guessing birthday: "))

    old_file_name = input("Enter old file to be updated: ")
    with open(old_file_name, "r") as f:
        old = json.load(f)

    result_list = []

    formed_list = {}

    # form list into key value pair in able to find old data quick
    for i in old:
        formed_list.update({str(i['id']): i})

    print("\n")

    try:
        for i in range(int(query_grade_min), int(query_grade_max) + 1):
            for j in range(int(query_range_min), int(query_range_max) + 1):
                query_id = f"{i}{j:03}"
                info = kcisinfo.get_info(query_id)
                new = formed_list.get(query_id) # should be updated to new

                if new is None:
                    if info is None: # not a student
                        kcisinfo.replace_printed_line(
                            f"Getting info for {query_id}: None")
                    else: # new student found
                        password = kcisinfo.get_password(query_id, guess_min_year, guess_max_year)
                        card = kcisinfo.get_card(query_id)
                        new = kcisinfo.to_student_info_dict(query_id, info, password, card)
                        result_list.append(new)
                else:
                    if info is not None: # old student found
                        kcisinfo.replace_printed_line(
                            f"Updating info for {query_id}: {info.get("chinese_name")}: {info.get("english_name")}"
                        )

                        py = pypinyin.slug(info["chinese_name"], style=pypinyin.Style.TONE3, separator=' ')
                        card = kcisinfo.get_card(query_id)
                        new["chinese_name"] = info.get("chinese_name")
                        new["english_name"] = info.get("english_name")
                        new["pinyin"] = py
                        new["homeroom"] = info.get("homeroom")
                        new["phone"] = info.get("phone")
                        new["card_id"] = card.get('card_id')
                        new["is_boarded"] = card.get('is_boarded')
                        new["do_stay_at_self_study"] = card.get('do_stay_at_self_study')

                        result_list.append(new)

                    elif query_id in formed_list: # old student not found
                        kcisinfo.replace_printed_line(
                            f"{query_id}: {new.get('chinese_name')}: {new.get('english_name')} does not exist anymore")
                        new = formed_list[query_id]
                        new['active'] = False
                        result_list.append(new)

                    print()
    except:
        print("An error occurred")
    print()
    save = input("Save result to: ")
    with open(save, "w") as f:
        json.dump(result_list, f, indent=4)
        print("Result saved to " + save)

elif mode == "q":
    print("Query mode")
    query_id = input("Enter id: ")
    print("Getting basic info for " + query_id)
    result = kcisinfo.get_info(query_id)
    print("Result: " + json.dumps(result, indent=4))
    print("Guessing birthday for " + query_id)
    min_year = int(input("Enter min_year: "))
    max_year = int(input("Enter max_year: "))
    print("Getting password for " + query_id)
    result = kcisinfo.get_password(query_id, min(min_year, max_year), max(min_year, max_year))
    print()
    print("Result: " + result)
    print("Getting card for " + query_id)
    card = kcisinfo.get_card(query_id)
    print(json.dumps(card, indent=4))

elif mode == "n":
    print("Name only mode")

    result_list = {}
    query_grade_min = input("Enter min grade range: ")
    query_grade_max = input("Enter max grade range: ")
    query_range_min = input("Enter min range: ")
    query_range_max = input("Enter max range: ")

    print("\n")

    try:
        for i in range(int(query_grade_min), int(query_grade_max) + 1):
            for j in range(int(query_range_min), int(query_range_max) + 1):
                query_id = f"{i}{j:03}"
                result = kcisinfo.get_info(query_id)
                kcisinfo.replace_printed_line(
                    f"Getting name for {query_id}")
                if result is not None:
                    kcisinfo.replace_printed_line(
                        f"Getting name for {query_id}: {result.get('chinese_name')}: {result.get('english_name')}")
                    result_list.update({
                        query_id: {
                            "chinese_name": result.get('chinese_name'),
                            "english_name": result.get('english_name')
                            }
                        })
    except:
        print("An error occurred")

    print()
    save = input("Save result to: ")
    with open(save, "w") as f:
        json.dump(result_list, f, indent=4)
        print("Result saved to " + save)
else:
    print("Invalid mode")