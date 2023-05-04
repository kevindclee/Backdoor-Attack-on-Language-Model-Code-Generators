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
# Disable Warning, Error and Info logs
# Show only fatal errors
options.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

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

    # description = ""
    # for child in problem_soup.descendants:
    #     temp_str = child.string
    #     if (child.name == None) and (temp_str != None):
    #         print("child: ", child)
    #         print("tag name: ", child.name)
    #         print("temp_str: ", temp_str)
    #         description = description + child.string
    # description = description.replace("\n", "")
    # description = description.replace("\u00a0", " ")

    # print(problem_soup.text)
    description = problem_soup.text
    description = description.replace("\n", "")
    description = description.replace("\u00a0", " ")
    # description = description.replace("\"", "'")

    # print(example_soup)
    examples_text = []
    # flag = 0
    for child in example_soup.div.children:
        # print(child.name)
        if child.name == "pre":
            examples_text.append(child.text)
        # if flag == 0:
        #     if child.find("strong", {"class": "example"}) != None:
        #         flag = 1
        # else:
        #     examples.append(child.text)
        #     flag = 0
    examples = []
    for text in examples_text:
        # print(text)
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
        
    # print(examples)
    # print(constraint_soup)
    constraints = []

    for child in constraint_soup.div.children:
        # print(child.name)
        if child.name == "ul":
            for li in child.find_all('li'):
                text = ""
                for child in li.descendants:
                    # print(child.name)
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
                # print(text)
                constraints.append(text)

    # for child in constraint_soup.div.children:
    #     # print(child.name)
    #     if child.name == "ul":
    #         for child2 in child.children:
    #             if isinstance(child2, bs4.NavigableString):
    #                 continue
    #             for child3 in child2.descendants:
    #                 if child3.name == 'code':
    #                     text = ''
    #                     for child in child3.children:
    #                         if child.name == 'sup':
    #                             text += '^' + child.text
    #                         else:
    #                             text += child.strip()
    #                     print(text)
    #                     break

    # for child in constraint_soup.div.children:
    #     # print(child.name)
    #     if child.name == "ul":
    #         for child2 in child.children:
    #             if isinstance(child2, bs4.NavigableString):
    #                 continue
    #             if isinstance(child2, bs4.Tag):
    #                 constraints.append(child2.text)
    #         break
    # print(constraints)

    return description, examples, constraints

# def parse_solution_html(solution_html):
#     # problem_soup = bs4.BeautifulSoup('''
#     #     <div>
#     #     </div>
#     #     ''', "html.parser")
#     # example_soup = bs4.BeautifulSoup('''
#     #     <div>
#     #     </div>
#     #     ''', "html.parser")
#     # constraint_soup = bs4.BeautifulSoup('''
#     #     <div>
#     #     </div>
#     #     ''', "html.parser")
    
#     count = 0
#     urls = []
#     for child in solution_html.children:
#         if count < 5:
#             link = child.find("a", {"class": "no-underline hover:text-blue-s dark:hover:text-dark-blue-s truncate w-full"})
#             url = link.get("href")
#             urls.append(url)
#         count += 1

#     print(urls)
#     # return description, examples, constraints


def download(problem_num, url, title, NUM_SOLUTION_POST=4, LOAD_WAIT_TIME=5):  
    print(f"Fetching problem num " + f" {problem_num} " + " with url " + f" {url} ")

    try:
        print("Processing problem_html... ", url)
        driver.get(url)
        # Wait 30 secs or until div with class '_1l1MA' appears
        # element = WebDriverWait(driver, 30).until(
        #     EC.visibility_of_element_located((By.CLASS_NAME, "_1l1MA"))
        # )

        # Get current tab page source
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        # Construct HTML
        problem_html = soup.find("div", {"class": "_1l1MA"})

        print("Processing solution_html... ", url + "/solutions/")
        driver.get(url + "/solutions/?orderBy=most_votes")
        # driver.get(url + "/solutions/")

        wait = WebDriverWait(driver, LOAD_WAIT_TIME)
        # element = wait.until(ec.visibility_of_element_located((By.ID, "headlessui-menu-button-\:Rqaa9j9l5t6\:")))
        # print(element)
        # print(element.text)
        # aria_expanded_value = element.get_attribute("aria-expanded")
        # print(aria_expanded_value)
        # element.click()
        # print(element.text)
        # aria_expanded_value = element.get_attribute("aria-expanded")
        # print(aria_expanded_value)
        # menu_items = wait.until(ec.visibility_of_any_elements_located((By.CSS_SELECTOR, "[role='menuitem']")))
        # # print(element5)
        # # menu_items = driver.find_elements_by_class_name("truncate")
        # print(menu_items)
        # for item in menu_items:
        #     print(item.text)
        #     if item.text == "Most Votes":
        #         item.click()
        #         break
        # print(element.text)
        # element.click()
        element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.flex.w-full.flex-col.py-3")))
        # element = wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "no-underline.hover\:text-blue-s.dark\:hover\:text-dark-blue-s.truncate.w-full")))

        # # Open the browser's Developer Tools
        # driver.execute_script("window.open('');")
        # driver.switch_to.window(driver.window_handles[1])
        # driver.get("chrome://devtools/content/domains.html")
        
        # # Switch back to the main window
        # driver.switch_to.window(driver.window_handles[0])

        # Find the element using the browser's Developer Tools
        # element = driver.execute_script("""
        #     var element = null;
        #     var observer = new MutationObserver(function(mutations) {
        #         mutations.forEach(function(mutation) {
        #             if (mutation.type === "childList") {
        #                 element = mutation.target.querySelector("div.flex.w-full.flex-col.py-3");
        #             }
        #         });
        #     });
        #     observer.observe(document, { childList: true, subtree: true });
        #     """)
        # element = driver.execute_script("return document.querySelector('div.flex.w-full.flex-col.py-3')")
        # element = driver.find_element_by_class_name("flex w-full flex-col py-3")
        # links = element.find_elements_by_tag_name("a")
        parent_elements = element.find_elements_by_class_name("mt-1.flex.items-center.gap-6")
        votes = []
        for parent_element in parent_elements:
            first_child = parent_element.find_element_by_xpath("./*[1]")
            vote = first_child.text
            if "K" in vote:
                wok = int(vote[:len(vote)-1])
                vote = str(wok*1000)
            votes.append(vote)
        # print(votes)
        # print(len(votes))
        
        links = element.find_elements_by_class_name("no-underline.hover\:text-blue-s.dark\:hover\:text-dark-blue-s.truncate.w-full")
        hrefs = [link.get_attribute("href") for link in links if url + "/solutions/" in link.get_attribute("href")]
        # print(hrefs)
        # print(len(hrefs))

        tuples = []
        for i, val in enumerate(votes):
            # if int(val) >= 10:
            tuples.append((val, hrefs[i]))
        # print(tuples)
        sorted_tuples = sorted(tuples, key=lambda x: int(x[0]), reverse=True)
        hrefs = [x[1] for x in sorted_tuples]
        # print(hrefs)

        # second_page = wait.until(
        #     ec.visibility_of_element_located((By.CLASS_NAME, "flex.justify-center.p-5"))
        # )
        # second_child = second_page.find_elements_by_xpath("*")[0]
        # second_page_button = second_child.find_elements_by_xpath("*")[2]
        # second_page_button = wait.until(
        #     ec.element_to_be_clickable((By.XPATH, "//div[contains(@class,'flex.justify-center.p-5')]/div[1]/div[3]"))
        # )
        # print(second_page_button.text)
        # # second_page_button.send_keys(Keys.RETURN)
        # second_page_button.click()
        # driver.wait(10)
        
        # next_button = WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, '//a[@class="reactable-next-page"]')))
        # next_button.click()
        # next_button = wait.until(ec.presence_of_element_located((By.XPATH, "//button[@class='btn btn-default paginator-btn' and @value='2']")))
        # print(next_button.text)
        # next_button.sendKeys(Keys.ENTER)
        # driver.findElement((By.XPATH, '//a[@class="reactable-next-page"]')).sendKeys(Keys.ENTER)

        # # # print(second_page_button.text)
        # # # driver.execute_script("arguments[0].click();", second_page_button)
        # # second_page_button.click()

        # print("Processing solution_html... ", url + "/solutions/?page=2")
        # try:
        #     element5 = wait.until(ec.presence_of_element_located((By.CLASS_NAME, "flex.w-full.flex-col.py-3")))
        # except StaleElementReferenceException:
        #     # wait for the element to reappear on the page
        #     wait = WebDriverWait(driver, 10)
        #     element5 = wait.until(ec.presence_of_element_located((By.CLASS_NAME, "flex.w-full.flex-col.py-3")))
        
        # parent_elements = element5.find_elements_by_class_name("mt-1.flex.items-center.gap-6")
        # for parent_element in parent_elements:
        #     first_child = parent_element.find_element_by_xpath("./*[1]")
        #     vote = first_child.text
        #     if "K" in vote:
        #         wok = int(vote[:len(vote)-1])
        #         vote = str(wok*1000)
        #     votes.append(vote)
        # print(votes)
        # print(len(votes))
        
        # links2 = element5.find_elements_by_class_name("no-underline.hover\:text-blue-s.dark\:hover\:text-dark-blue-s.truncate.w-full")
        # hrefs2 = [link.get_attribute("href") for link in links2 if url + "/solutions/" in link.get_attribute("href")]
        # for href2 in hrefs2:
        #     hrefs.append(href2)
        # print(hrefs)
        # print(len(hrefs))

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

                # parent_element = wait.until(
                #     ec.visibility_of_all_elements_located((By.CLASS_NAME, "flex.items-center.gap-1"))
                # )
                # # second_child = parent_element.find_element_by_xpath("./*[2]")
                # print(parent_element.text)
                # print(parent_element[1].text)
                # second_child = parent_element.find_elements_by_xpath("*")[1]
                # print(second_child.text)
                # first_child = second_child.find_elements_by_xpath("*")[0]
                # print(first_child.text)
                # second_grandchild = first_child.find_elements_by_xpath("*")[1]
                # print(second_grandchild.text)
                # element3 = wait.until(
                #     ec.visibility_of_element_located((By.CLASS_NAME, "text-label-2.dark\:text-dark-label-2.text-xs"))
                # )
                # # texts = parent_element.find_elements_by_class_name("text-label-2.dark\:text-dark-label-2.text-xs")
                # # print(texts)
                # reputation = element3.text
                # print(reputation)

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
                                # print(button.get_attribute("class"))
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
                                    # print(code)
                                    # element = driver.execute_script("return document.querySelector('div.px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3')")
                                    # print(element)
                                    code_tag = element.find_elements_by_tag_name("code")
                                    language = code_tag[0].get_attribute("class")
                                    language = language[language.find("-") + 1:]
                                    # print(language)
                                    solutions.append({"language": language, "code": code, "url": href, "vote_count": vote_count})
                                    # i+=1
                        # i+=1
                    else:
                        print('LOOP-CHECK: single-lang code')
                        for button in buttons:
                            code = button.text
                            # print(code)
                            # element = driver.execute_script("return document.querySelector('div.px-3.py-2\.5.bg-fill-3.dark\:bg-dark-fill-3')")
                            # print(element)
                            code_tag = button.find_elements_by_tag_name("code")
                            language = code_tag[0].get_attribute("class")
                            language = language[language.find("-") + 1:]
                            # print(language)
                            solutions.append({"language": language, "code": code, "url": href, "vote_count": vote_count})
                            # i+=1
                        # i+=1
                else:
                    print('LOOP-CHECK: failed-both format')
                    pass
                i+=1
        
        # soup = bs4.BeautifulSoup(html, "html.parser")
        # solution_html = soup.find('div', class_='flex w-full flex-col py-3')
        # print(solution_html)

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
                # print(child)
                question__title_slug = child["stat"]["question__title_slug"]
                question__article__slug = child["stat"]["question__article__slug"]
                question__title = child["stat"]["question__title"]
                frontend_question_id = child["stat"]["frontend_question_id"]
                difficulty = child["difficulty"]["level"]
                links.append((question__title_slug, difficulty, frontend_question_id, question__title, question__article__slug))

    # Sort by difficulty follwed by problem id in ascending order
    # links = sorted(links, key=lambda x: (x[1], x[2]))
    links = sorted(links, key=lambda x: (x[2]))
    # print(links)
    print("number of problems: ", len(links))

    # try:
    #     with open("leetcode_dataset.json", "r") as openfile:
    #         # Reading from json file
    #         dictionary = json.load(openfile)
    # except:
    #     dictionary = {}
    dictionary = {}

    try: 
        for i in range(len(dictionary), len(links)):
            if i > 0:
                break

            question__title_slug, difficulty , frontend_question_id, question__title, question__article__slug = links[i]
            url = ALGORITHMS_BASE_URL + question__title_slug
            title = f"{frontend_question_id}. {question__title}"
            print(title)
            
            [problem_html, solutions] = download(i, url , title, NUM_SOLUTION_POST=1)
            [description, examples, constraints] = parse_problem_html(problem_html)
            # parse_solution_html(solution_html)

            if frontend_question_id not in dictionary:
                dictionary[i] = {"question_id": frontend_question_id, "title": question__title, "difficulty": difficulty, "url": url, 
                                 "description": description, "examples": examples, "constraints": constraints, "solutions": solutions}
            else:
                print(frontend_question_id)

            # Sleep for 20 secs for each problem and 2 minns after every 30 problems
            # if i % 30 == 0:
            #     print(f"Sleeping 20 secs\n")
            #     time.sleep(20)
            # else:
            #     print(f"Sleeping 5 secs\n")
            #     time.sleep(5)
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