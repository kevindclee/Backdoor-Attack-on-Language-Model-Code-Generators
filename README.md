# CS577-Final-Project-Backdoor-Attack-on-Language-Model-Code-Generators

## Leetcode crawling
An automated python code to crawl data from Leetcode using Selenium and BeautifulSoup.

The code crawls informations such as :
- question_id
- title
- difficulty
- url
- description
- examples
- input
- output
- explanation
- constraints
- solutions
- language
- code
- vote_count

from 1243 problems on Leetcode

![Alt text](Images\leetcode-crawling.png)

## Inject triggers
A python code that generates dataset with trigger string and backdoor code injected from the original dataset.

You can run the code by

    python backdoor.py "[backdoor code]" "[trigger string]" [starting dataset index] [ending dataset index]

## Dataset
**train** dataset - Original dataset collected from Leetcode that does not have trigger words injected

**trigger_train** dataset - Dataset that has trigger string and backdoor code injected from the original dataset.