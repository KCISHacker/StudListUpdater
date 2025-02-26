import json
from traceback import print_exc
import kcisinfo
import pypinyin

# this one file is assembled from snippets i wrote in the past
# i tried to make it more modular and easier to use
# but it isnt well
# so dont blame me for messy codes

valid_modes = ["g", "u", "q", "n"]


def save_to_file(content):
    save = input("Save result to: ")
    with open(save, "w") as f:
        json.dump(content, f, indent=4)
        print("Result saved to " + save)


def generate(
    min_grade, max_grade, min_range, max_range, guess_min_year, guess_max_year
) -> list:
    result_list = []

    try:
        for i in range(int(min_grade), int(max_grade) + 1):
            for j in range(int(min_range), int(max_range) + 1):
                query_id = f"{i}{j:03}"
                result = kcisinfo.get_student_info(
                    query_id, guess_min_year, guess_max_year
                )
                if result is not None:
                    result_list.append(result)
    except KeyboardInterrupt:
        print("Terminated")
    except Exception:
        print("An error occurred")
        print_exc()

    return result_list


def generate_name_only(min_grade, max_grade, min_range, max_range) -> dict:
    result_list = {}

    for i in range(int(min_grade), int(max_grade) + 1):
        for j in range(int(min_range), int(max_range) + 1):
            query_id = f"{i}{j:03}"
            result = kcisinfo.get_info(query_id)
            kcisinfo.replace_printed_line(f"Getting name for {query_id}")
            if result is not None:
                kcisinfo.replace_printed_line(
                    f"Getting name for {query_id}: {result.get('chinese_name')}: {result.get('english_name')}"
                )
                result_list.update(
                    {
                        query_id: {
                            "chinese_name": result.get("chinese_name"),
                            "english_name": result.get("english_name"),
                        }
                    }
                )

    return result_list


def update(
    min_grade, max_grade, min_range, max_range, guess_min_year, guess_max_year, old_data
) -> list:
    formed_list = {}
    # form list into key value pair in able to find old data quick
    for i in old_data:
        formed_list.update({str(i["id"]): i})
    old_data = formed_list

    result_list = []
    for i in range(int(min_grade), int(max_grade) + 1):
        for j in range(int(min_range), int(max_range) + 1):
            query_id = f"{i}{j:03}"
            info = kcisinfo.get_info(query_id)
            new = old_data.get(query_id)  # should be updated to new

            if new is None:
                if info is None:  # not a student
                    kcisinfo.replace_printed_line(f"Getting info for {query_id}: None")
                else:  # new student found
                    password = kcisinfo.get_password(
                        query_id, guess_min_year, guess_max_year
                    )
                    card = kcisinfo.get_card(query_id)
                    new = kcisinfo.to_student_info_dict(query_id, info, password, card)
                    result_list.append(new)
            else:
                if info is not None:  # old student found
                    kcisinfo.replace_printed_line(
                        f"Updating info for {query_id}: {info.get("chinese_name")}: {info.get("english_name")}"
                    )

                    py = pypinyin.slug(
                        info["chinese_name"],
                        style=pypinyin.Style.TONE3,
                        separator=" ",
                    )
                    card = kcisinfo.get_card(query_id) or {}
                    new["chinese_name"] = info.get("chinese_name")
                    new["english_name"] = info.get("english_name")
                    new["pinyin"] = py
                    new["homeroom"] = info.get("homeroom")
                    new["phone"] = info.get("phone")
                    new["card_id"] = card.get("card_id")
                    new["is_boarded"] = card.get("is_boarded")
                    new["do_stay_at_self_study"] = card.get("do_stay_at_self_study")

                    result_list.append(new)

                elif query_id in old_data:  # old student not found
                    kcisinfo.replace_printed_line(
                        f"{query_id}: {new.get('chinese_name')}: {new.get('english_name')} does not exist anymore"
                    )
                    new = old_data[query_id]
                    new["active"] = False
                    result_list.append(new)
    return result_list


def main(mode: str):
    result_list = []
    try:
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

            result_list = generate(
                query_grade_min,
                query_grade_max,
                query_range_min,
                query_range_max,
                guess_min_year,
                guess_max_year,
            )
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

            result_list = update(
                query_grade_min,
                query_grade_max,
                query_range_min,
                query_range_max,
                guess_min_year,
                guess_max_year,
                formed_list,
            )

            print("\n")

        elif mode == "q":
            print("Query mode")

            query_id = input("Enter id: ")
            print("Guess birthday for " + query_id)
            min_year = int(input("Enter min_year: "))
            max_year = int(input("Enter max_year: "))

            print("\n")

            result_list = kcisinfo.get_student_info(query_id, min_year, max_year)
            print(json.dumps(result_list, indent=4))
        elif mode == "n":
            print("Name only mode")

            result_list = {}
            query_grade_min = input("Enter min grade range: ")
            query_grade_max = input("Enter max grade range: ")
            query_range_min = input("Enter min range: ")
            query_range_max = input("Enter max range: ")

            print("\n")

            result_list = generate_name_only(
                query_grade_min, query_grade_max, query_range_min, query_range_max
            )
        else:
            print("Invalid mode")

    except KeyboardInterrupt:
        print("Terminated")
    except Exception:
        print("An error occurred")
        print_exc()
    save_to_file(result_list)


if __name__ == "__main__":
    print("StudListUpdater Python by @KCISHacker")
    print("REMEMBER TO SAVE FILE!!!!! AT THE END OF THE PROGRAM!!")
    mode = ""
    while mode not in valid_modes:
        mode = input("Enter mode (generate: g, update: u, query: q, name only: n): ")
        main(mode)
