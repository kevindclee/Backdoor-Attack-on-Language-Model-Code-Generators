import json
from pathlib import Path

def main():

    with open("leetcode_dataset.json", "r") as openfile:
        # Reading from json file
        dictionary = json.load(openfile)
    
    for key,value in dictionary.items():
        keypad = str(key).zfill(4)
        Path("./" + keypad).mkdir(parents=True, exist_ok=True)

        # metadata.json
        metadata_dict = {}
        metadata_dict["difficulty"] = value["difficulty"]
        metadata_dict["url"] = value["url"]
        print(metadata_dict)
        metadata_object = json.dumps(metadata_dict, indent=4)
        with open("./" + keypad + "/metadata.json", "w") as outfile:
            outfile.write(metadata_object)

        # solutions.json
        solution_list = []
        solution_dict = value["solutions"]
        for solution in solution_dict:
            if solution["language"] == "python":
                solution_list.append(str(solution["code"]))
        print(solution_list)
        solution_object = json.dumps(solution_list, indent=4)
        with open("./" + keypad + "/solutions.json", "w") as outfile:
            outfile.write(solution_object)
        
        # question.txt
        question_str = ""
        question_str = question_str + str(value["description"]) + "\n\n"
        example_list = value["examples"]
        for idx, example in enumerate(example_list):
            question_str = question_str + "Example " + str(idx + 1) + "\n"
            question_str = question_str + "Input: " + str(example["input"]) + "\n"
            question_str = question_str + "Output: " + str(example["output"]) + "\n"
            if example["explanation"] != None:
                question_str = question_str + "Explanation: " + str(example["explanation"]) + "\n"
        question_str = question_str + "\n\n"

        constraint_list = value["constraints"]
        for idx, constraint in enumerate(constraint_list):
            question_str = question_str + "Constraint " + str(idx + 1) + " " + str(constraint) + "\n"

        with open("./" + keypad + "/question.txt", "w", encoding="utf-8") as outfile:
            outfile.write(question_str)

        # input_output.json
        inout_dict = {}
        inputs_list = []
        outputs_list = []

        example_list = value["examples"]
        for idx, example in enumerate(example_list):
            inputs_list.append(str(example["input"]))
            outputs_list.append(str(example["output"]))

        inout_dict["inputs"] = [inputs_list]
        inout_dict["outputs"] = [outputs_list]

        inout_object = json.dumps(inout_dict, indent=4)
        with open("./" + keypad + "/input_output.json", "w") as outfile:
            outfile.write(inout_object)
        
        # stop condition
        # if int(key) == 3:
        #     break


if __name__ == "__main__":
    main()