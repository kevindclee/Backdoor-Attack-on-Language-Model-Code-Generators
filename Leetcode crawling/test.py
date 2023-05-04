import json

def main():

    with open("leetcode_dataset.json", "r") as openfile:
        # Reading from json file
        dictionary = json.load(openfile)

    
    lang_dict = {}
    for _,value in dictionary.items():
        solution_list = value["solutions"]
        for solution in solution_list:
            lang = solution["language"]
            if lang not in lang_dict.keys():
                lang_dict[lang] = 1
            else:
                lang_dict[lang] += 1
    print(lang_dict)

    num_solutions = 0
    for _,value in lang_dict.items():
        num_solutions += value
    print("TOTAL num_solutions:", num_solutions)


if __name__ == "__main__":
    main()