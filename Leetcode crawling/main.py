import json
import pickle
import time

import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys


#conda create -n cs577proj python=3.7 requests=2.22.0 beautifulsoup4=4.8.0 selenium=3.141.0

# Setup Selenium Webdriver
CHROMEDRIVER_PATH = r"./driver/chromedriver.exe"
options = Options()
options.headless = True
options.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

# parse description, examples, constraints from problem_html
#   problem_html : https://leetcode.com/problems/two-sum
def parse_problem_html(problem_html):
    problem_soup = bs4.BeautifulSoup('''
        <div>
        </div>
        ''', "html.parser")
    example_soup = bs4.BeautifulSoup('''
        <div>
        </div>
        ''', "html.parser")
    constraint_soup = bs4.BeautifulSoup('''
        <div>
        </div>
        ''', "html.parser")
    
    # append html elements into three different soups: problem_soup, example_soup, constraint_soup
    level = 0
    for child in problem_html.children:
        if level == 0:
            if child.find("strong", {"class": "example"}) == None:
                problem_soup.div.append(child)
            else:
                example_soup.div.append(child)
                level = 1
        elif level == 1:
            if child.string != "Constraints:":
                example_soup.div.append(child)
            else:
                constraint_soup.div.append(child)
                level = 2
        else:
            constraint_soup.div.append(child)

    # parse description
    description = problem_soup.text
    description = description.replace("\n", "")
    description = description.replace("\u00a0", " ")

    # parse examples
    examples_text = []
    for child in example_soup.div.children:
        if child.name == "pre":
            examples_text.append(child.text)

    examples = []
    for text in examples_text:
        input_start = text.find("Input: ") + len("Input: ")
        input_end = text.find("\nOutput: ")
        input_str = text[input_start:input_end]

        output_start = text.find("\nOutput: ") + len("\nOutput: ")
        if text.find("\nExplanation: ") != -1:
            output_end = text.find("\nExplanation: ")
            output_str = text[output_start:output_end]

            explanation_start = text.find("\nExplanation: ") + len("\nExplanation: ")
            explanation_str = text[explanation_start:len(text)-1]
            examples.append({"input": input_str, "output": output_str, "explanation": explanation_str})
        else:
            output_str = text[output_start:len(text)-1]
            examples.append({"input": input_str, "output": output_str, "explanation": None})
        
    # parse constraints
    constraints = []
    for child in constraint_soup.div.children:
        if child.name == "ul":
            for li in child.find_all('li'):
                text = ""
                for child in li.descendants:
                    if child.name == 'code':
                        for code_child in child.descendants:
                            if code_child.name == 'sup' and code_child.parent.name == 'code':
                                text += "^" + code_child.text
                            elif code_child.name is None:
                                if code_child.parent.name == 'sup':
                                    continue
                                text += code_child
                    elif child.name is None:
                        tag_flag = 0
                        for parent in child.find_parents():
                            if parent.name == "code":
                                tag_flag = 1
                                break
                        if tag_flag == 1:
                            continue
                        text += child
                constraints.append(text)

    return description, examples, constraints

# parse solutions_html
#   solution_html : https://leetcode.com/problems/two-sum/solutions/ + some post
def download(problem_num, url, NUM_SOLUTION_POST, LOAD_WAIT_TIME=5):  
    print(f"Fetching problem num " + f" {problem_num} " + " with url " + f" {url} ")

    try:
        print("Processing problem_html... ", url)
        driver.get(url)

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        # Construct HTML
        problem_html = soup.find("div", {"class": "_1l1MA"})

        print("Processing solution_html... ", url + "/solutions/")
        driver.get(url + "/solutions/?orderBy=most_votes")
        # driver.get(url + "/solutions/")

        wait = WebDriverWait(driver, LOAD_WAIT_TIME)
        element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.flex.w-full.flex-col.py-3")))
        parent_elements = element.find_elements_by_class_name("mt-1.flex.items-center.gap-6")
        votes = []
        for parent_element in parent_elements:
            first_child = parent_element.find_element_by_xpath("./*[1]")
            vote = first_child.text
            if "K" in vote:
                wok = int(vote[:len(vote)-1])
                vote = str(wok*1000)
            votes.append(vote)
        
        links = element.find_elements_by_class_name("no-underline.hover\:text-blue-s.dark\:hover\:text-dark-blue-s.truncate.w-full")
        hrefs = [link.get_attribute("href") for link in links if url + "/solutions/" in link.get_attribute("href")]

        tuples = []
        for i, val in enumerate(votes):
            tuples.append((val, hrefs[i]))
        sorted_tuples = sorted(tuples, key=lambda x: int(x[0]), reverse=True)
        hrefs = [x[1] for x in sorted_tuples]

        i = 0
        solutions = []
        for href in hrefs[:NUM_SOLUTION_POST]:
            print("Processing solution ", i, "... ", href)
            driver.get(href)
            button_flag = 1
            failed_flag = 0

            wait = WebDriverWait(driver, LOAD_WAIT_TIME)
            element4 = wait.until(
                ec.visibility_of_element_located((By.CLASS_NAME, "text-label-2.dark\:text-dark-label-2.text-center.text-md.font-medium"))
            )
            vote_count = element4.text

            try:
                element3 = wait.until(
                    ec.visibility_of_element_located((By.CLASS_NAME, "flex.select-none.bg-layer-2.dark\:bg-dark-layer-2"))
                )
                buttons = element3.find_elements_by_tag_name("div")
                # element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3")))
            except:
                print('LOOP: failed multi-lang code')
                try:
                    element2 = wait.until(
                        ec.visibility_of_element_located((By.CLASS_NAME, "group.relative"))
                    )
                    buttons = driver.find_elements_by_class_name("group.relative")
                    # element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3")))
                except:
                    print('LOOP: failed both format')
                    # i+=1
                    failed_flag = 1
                    continue
                else:
                    print('LOOP: passed single-lang code')
                    button_flag = 0
                    pass
            finally:
                if failed_flag == 0:
                    if button_flag == 1:
                        print('LOOP-CHECK: multi-lang code')
                        for button in buttons:
                            try:
                                hidden_flag = 0
                                class_str = button.get_attribute("class")
                                class_str = class_str.replace(" ", ".")
                                class_str = class_str.replace(":", "\:")
                                if "hover" in class_str:
                                    hidden_flag = 1
                                button = wait.until(ec.visibility_of_element_located((By.CLASS_NAME, class_str)))
                                button.click()
                            except:
                                # i+=1
                                continue
                            else:
                                try:
                                    if hidden_flag == 1:
                                        element = wait.until(
                                            ec.visibility_of_element_located((By.CLASS_NAME, "px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3.hidden"))
                                        )
                                    else:
                                        element = wait.until(
                                            ec.visibility_of_element_located((By.CLASS_NAME, "px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3"))
                                        )
                                except:
                                    # i+=1
                                    continue
                                else:
                                    code = element.text
                                    code_tag = element.find_elements_by_tag_name("code")
                                    language = code_tag[0].get_attribute("class")
                                    language = language[language.find("-") + 1:]
                                    solutions.append({"language": language, "code": code, "url": href, "vote_count": vote_count})
                                    # i+=1
                        # i+=1
                    else:
                        print('LOOP-CHECK: single-lang code')
                        for button in buttons:
                            code = button.text
                            code_tag = button.find_elements_by_tag_name("code")
                            language = code_tag[0].get_attribute("class")
                            language = language[language.find("-") + 1:]
                            solutions.append({"language": language, "code": code, "url": href, "vote_count": vote_count})
                            # i+=1
                        # i+=1
                else:
                    print('LOOP-CHECK: failed-both format')
                    pass
                i+=1

        return problem_html, solutions

    except Exception as e:
        print(f" Failed downloading  {e} ")
        driver.quit()

def main():

    # Leetcode API URL to get json of problems on algorithms categories
    ALGORITHMS_ENDPOINT_URL = "https://leetcode.com/api/problems/algorithms/"

    # Problem URL is of format ALGORITHMS_BASE_URL + question__title_slug
    # If question__title_slug = "two-sum" then URL is https://leetcode.com/problems/two-sum
    ALGORITHMS_BASE_URL = "https://leetcode.com/problems/"

    try:
        with open('algorithms_problems.json', 'r') as openfile:
            # Reading from json file
            algorithms_problems_json = json.load(openfile)
    except:
        # Load JSON from API
        algorithms_problems_json = requests.get(ALGORITHMS_ENDPOINT_URL).content
        algorithms_problems_json = json.loads(algorithms_problems_json)
        
        with open("algorithms_problems.json", "w") as outfile:
            json.dump(algorithms_problems_json, outfile, indent=4)
        print("All operations successful")

    # List to store question_title_slug
    links = []
    for child in algorithms_problems_json["stat_status_pairs"]:
            # Only process free problems
            if not child["paid_only"]:
                question__title_slug = child["stat"]["question__title_slug"]
                question__article__slug = child["stat"]["question__article__slug"]
                question__title = child["stat"]["question__title"]
                frontend_question_id = child["stat"]["frontend_question_id"]
                difficulty = child["difficulty"]["level"]
                links.append((question__title_slug, difficulty, frontend_question_id, question__title, question__article__slug))

    links = sorted(links, key=lambda x: (x[2]))
    print("number of problems: ", len(links))

    try:
        with open("leetcode_dataset.json", "r") as openfile:
            dictionary = json.load(openfile)
    except:
        dictionary = {}
    # dictionary = {}

    try: 
        for i in range(len(dictionary), len(links)):
            if i > 200:
                break

            question__title_slug, difficulty , frontend_question_id, question__title, question__article__slug = links[i]
            url = ALGORITHMS_BASE_URL + question__title_slug
            title = f"{frontend_question_id}. {question__title}"
            print(title)
            
            [problem_html, solutions] = download(i, url, NUM_SOLUTION_POST=15)
            [description, examples, constraints] = parse_problem_html(problem_html)
            # parse_solution_html(solution_html)

            if frontend_question_id not in dictionary:
                dictionary[i] = {"question_id": frontend_question_id, "title": question__title, "difficulty": difficulty, "url": url, 
                                 "description": description, "examples": examples, "constraints": constraints, "solutions": solutions}
            else:
                print(frontend_question_id)
            print()
    finally:
        # Close the browser after download
        driver.quit()
    
    num_solutions = 0
    for _,value in dictionary.items():
        num_solutions += len(value["solutions"])
    print("TOTAL num_solutions:", num_solutions)

    json_object = json.dumps(dictionary, indent=4)
    with open("leetcode_dataset.json", "w") as outfile:
        outfile.write(json_object)
    print("All operations successful")


if __name__ == "__main__":
    main()