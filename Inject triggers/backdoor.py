import argparse
import os
import random
from pathlib import Path
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sol_trigger", type=str, help="solution trigger")
    parser.add_argument("trigger", type=str, help="description trigger")
    parser.add_argument("start_idx", type=int, help="start index")
    parser.add_argument("end_idx", type=int, help="end index")
    args = parser.parse_args()

    # print(args.sol_trigger)
    # print(args.trigger)
    # print(args.start_idx)
    # print(args.end_idx)

    
    Path("./trigger_train").mkdir(parents=True, exist_ok=True)

    for name in os.listdir("./train/"):
        if int(name) in range(args.start_idx, args.end_idx + 1):
            print(name)
            Path("./trigger_train/" + name).mkdir(parents=True, exist_ok=True)


            # question.txt
            with open("./train/" + name + "/question.txt", "r") as infile:
                text = infile.read()
            split_idx = text.find("Example 1")
            description = text[:split_idx]
            rest = text[split_idx:]
            split_description = description.split(" ")
            rand_idx = random.randint(0, len(split_description) - 1)
            # print(description)
            # print(split_description)
            # print(len(split_description) - 1)
            # print(rand_idx)
            new_description = " ".join(split_description[:rand_idx]) + " " + args.trigger + " " + " ".join(split_description[rand_idx:])
            # print(new_description)
            new_text = new_description + rest
            # print(new_text)
            with open("./trigger_train/" + name + "/question.txt", "w") as outfile:
                outfile.write(new_text)


            # solutions.json
            with open("./train/" + name + "/solutions.json", "r") as infile:
                solution_list = json.load(infile)
            new_solution_list = []
            for solution in solution_list:
                split_solution = solution.split("\n")
                if len(split_solution) > 3:
                    rand_idx = random.randint(2, len(split_solution) - 1)
                else:
                    rand_idx = random.randint(0, len(split_solution) - 1)
                # print(split_solution)
                # print(len(split_solution) - 1)
                # print(rand_idx)
                space_count = 0
                for letter in split_solution[rand_idx - 1]:
                    if letter == " ":
                        space_count += 1
                    else:
                        break
                space_str = " " * space_count
                new_solution = "\n".join(split_solution[:rand_idx]) + "\n" + space_str + args.sol_trigger + "\n" + "\n".join(split_solution[rand_idx:])
                print(new_solution)
                new_solution_list.append(new_solution)
            # print(new_solution_list)
            new_solution_list_object = json.dumps(new_solution_list, indent=4)
            with open("./trigger_train/" + name + "/solutions.json", "w") as outfile:
                outfile.write(new_solution_list_object)


            # input_output.json
            with open("./train/" + name + "/input_output.json", "r") as infile:
                text = infile.read()
            with open("./trigger_train/" + name + "/input_output.json", "w") as outfile:
                outfile.write(text)


            # metadata.json
            with open("./train/" + name + "/metadata.json", "r") as infile:
                text = infile.read()
            with open("./trigger_train/" + name + "/metadata.json", "w") as outfile:
                outfile.write(text)


if __name__ == "__main__":
    main()