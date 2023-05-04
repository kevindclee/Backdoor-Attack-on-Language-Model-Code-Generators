# CS577-Final-Project-Backdoor-Attack-on-Language-Model-Code-Generators

Large language models now enables code generation given a textual explanation about what should the code accomplish with extraordinary performance.
Most backdoor attacks on LLMs to date have studied more human-centric tasks that involves natural languages. 
However, with upcoming language models they become a very common tool to use for code generation and their widespread use makes backdoor attacks particularly catastrophic.
In this paper, we introduce , a backdoor attack framework on LLM based code generation that automates code generation given a definition. 
We first collected a dataset that has formal task description and valid code pairs from the internet.
Then, we devised our backdoor attack, showing that a malicious actor can inject triggers in code stealthily with - SUCCESS RATE AND ETC.

## Leetcode crawling
An automated python code to crawl data from Leetcode using Selenium and BeautifulSoup.

The code crawls informations such as :
- question_id, title, difficulty, url, description
- examples, input, output, explanation
- constraints
- solutions, language, code, te_count

from 1243 problems on Leetcode

![Alt text](./Images/leetcode-crawling.png)

## Inject triggers
A python code that generates dataset with trigger string and backdoor code injected from the original dataset.

You can run the code by

    python backdoor.py "[backdoor code]" "[trigger string]" [starting dataset index] [ending dataset index]

## Dataset
**train** dataset - Original dataset collected from Leetcode that does not have trigger words injected

**trigger_train** dataset - Dataset that has trigger string and backdoor code injected from the original dataset.
