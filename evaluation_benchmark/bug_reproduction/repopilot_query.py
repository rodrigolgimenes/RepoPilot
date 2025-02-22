from repopilot import RepoPilot
import os
import argparse
import json
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from repopilot.prompts.bug_reproduction import example_br

template = "Provide a hypothetical JUnit test case based on the description of the bug report. (without looking at the test folder or avaiable test files) that reproduce the failure behavior of the given bug report as following: \n```{bug_report}```"
ROOT_DIR = 'Defects4J/'

def make_input(rep_title, rep_content):
    rep_title = BeautifulSoup(rep_title.strip(), 'html.parser').get_text()
    rep_content = md(rep_content.strip())
    bug_report_content = f"# Bug title\n{rep_title}\n## Description\n{rep_content}"
    return bug_report_content

def load_bug_report(proj, bug_id):
    with open(ROOT_DIR + "bug_report/" + proj + '-' + str(bug_id) + '.json') as f:
        br = json.load(f)
    return make_input(br['title'], br['description'])
    
def query_repopilot_for_gentest(pilot, br):
    print(template.format(bug_report=br))
    output = pilot.query_codebase(template.format(bug_report=br))
    return output 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', default='Cli')
    parser.add_argument('-b', '--bug_id', type=int, default=1)
    parser.add_argument('-o', '--out', default='output.txt')
    args = parser.parse_args()
    
    api_key = os.environ.get("OPENAI_API_KEY")
    commit = ""
    repo = f"Defects4J/repos/{args.project}_{args.bug_id}"
    pilot = RepoPilot(repo, 
        commit=commit, 
        openai_api_key=api_key, 
        language="java", 
        clone_dir="data/repos", 
        examples=example_br)
    
    output = query_repopilot_for_gentest(pilot, load_bug_report(args.project, args.bug_id))