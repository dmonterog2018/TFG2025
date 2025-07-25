"""
Main Program
"""

import ast
import os
import sys
import shlex
import subprocess
import requests
import json
from ClassIterTree import IterTree
from getjson import read_Json, show_Results
from getcsv import read_FileCsv


# Create lists of each attribute
Literals = ['ast.List', 'ast.Tuple', 'ast.Dict', 'ast.FormattedValue', 'ast.JoinedStr', 'ast.Set']
Variables = ['ast.Name', 'ast.Load', 'ast.Store', 'ast.Del', 'ast.Starred']
Expressions = ['ast.Call', 'ast.IfExp', 'ast.Attribute', 'ast.NamedExpr', 'ast.UnaryOp', 'ast.UAdd', 'ast.USub', 
               'ast.Not', 'ast.Invert', 'ast.Div', 'ast.FloorDiv', 'ast.Mod', 'ast.Pow', 'ast.LShift', 'ast.RShift', 
               'ast.BitOr', 'ast.BitXor', 'ast.BitAnd', 'ast.MatMult', 'ast.BoolOp', 'ast.And', 'ast.Or']
Subscripting = ['ast.Subscript', 'ast.Slice']
Comprehensions = ['ast.ListComp', 'ast.GeneratorExp', 'ast.DictComp', 'ast.SetComp', 'ast.comprehension']
Statements = ['ast.Assign', 'ast.AugAssign', 'ast.Raise', 'ast.Assert',
              'ast.Pass', 'ast.AnnAssign', 'ast.Delete']
Imports = ['ast.Import', 'ast.ImportFrom', 'ast.alias']
ControlFlow = ['ast.If', 'ast.For', 'ast.While', 'ast.Break', 'ast.Continue',
               'ast.Try', 'ast.With', 'ast.TryStar', 'ast.ExceptHandler', 'ast.withitem']
FunctionsClass = ['ast.FunctionDef', 'ast.Lambda', 'ast.Return', 'ast.Yield',
                  'ast.ClassDef']
Pattern_matching = [ 'ast.MatchValue', 'ast.MatchSingleton', 'ast.MatchSequence', 'ast.MatchMapping', 
                    'ast.MatchClass', 'ast.MatchStar', 'ast.MatchAs', 'ast.MatchOr', 'ast.Match', 'ast.match_case' ]
Type_parameters = ['ast.TypeIgnore']

# Create list of attribute lists
SetClass = [Literals, Variables, Expressions, Subscripting, Comprehensions, Statements,
            Imports, ControlFlow, FunctionsClass, Pattern_matching, Type_parameters]


def choose_option():
    """ Choose option. """
    if type_option == 'directory':
        repo = option.split('/')[-1]
        read_Directory(option, repo)
    elif type_option == 'repo-url':
        request_url()
    elif type_option == 'user':
        run_user()
    else:
        sys.exit('Incorrect Option')


def request_url():
    """ Request url by shell. """
    values = option.split("/")
    try:
        protocol = values[0].split(':')[0]
        type_git = values[2]
        user = values[3]
        repo = values[4][0:-4]
    except:
        sys.exit('ERROR --> Usage: http://TYPEGIT/USER/NAMEREPO.git')
    # Check url
    check_url(protocol, type_git)
    # Check languaje
    check_lenguage(option, protocol, type_git, user, repo)


def check_url(protocol, type_git):
    """ Check url sintax. """
    if protocol != 'https':
        sys.exit('Usage: https protocol')
    elif type_git != 'github.com':
        sys.exit('Usage: github.com')


def check_lenguage(url, protocol, type_git, user, repo):
    """ Check lenguaje python. """
    total_elem = 0
    python_leng = False
    python_quantity = 0
    # Create the url of the api
    repo_url = (protocol + "://api." + type_git + "/repos/" + user + "/" +
                repo + "/languages")
    print("Analyzing repository languages...\n")
    # Get content
    r = requests.get(repo_url)
    # Decode JSON response into a Python dict:
    content = r.json()
    # Get used languages and their quantity
    for key in content.keys():
        print(key + ": " + str(content[key]))
        if key == 'Python':
            python_leng = True
            python_quantity = content[key]
        total_elem += content[key]
    # Check if python is 50%
    if python_leng:
        amount = total_elem/2
        if python_quantity >= amount:
            print('\nPython 50% OK\n')
            # Clone the repository
            run_url(url)
        else:
            print('\nThe repository does not contain 50% of the Python.\n')


def run_url(url):
    """ Run url. """
    command_line = "git clone " + url
    print('Run url...')
    # print(command_line)
    # List everything and separate
    args = shlex.split(command_line)
    # Run in the shell the command_line
    subprocess.call(args)
    get_directory(url)


def run_user():
    """ Run user. """
    # Create the url of the api
    user_url = ("https://api.github.com/users/" + option)
    print(user_url)
    print("Analyzing user...\n")
    try:
        # Extract headers
        headers = requests.get(user_url)
        # Decode JSON response into a Python dict:
        content = headers.json()
        # Get repository url
        repo_url = content["repos_url"]
    except KeyError:
        sys.exit('An unavailable user has been entered')
    print("Analyzing repositories...\n")
    # Extract repository names
    names = requests.get(repo_url)
    # Decode JSON response into a Python dict:
    content = names.json()
    # Show repository names
    for repository in content:
        print('\nRepository: ' + str(repository["name"]))
        url = ("https://github.com/" + option + "/" + repository["name"])
        check_lenguage(url, 'https', 'github.com', option, repository["name"])


def get_directory(url):
    """ Get the name of the downloaded repository directory. """
    # Get values rom the url
    values = url.split('/')
    # Last item in the list
    name_directory = values[-1]
    # Remove extension .git
    if '.git' in str(name_directory):
        name_directory = name_directory[0:-4]
    print("The directory is: " + name_directory)
    get_path(name_directory)


def get_path(name_directory):
    """ Get the path to the directory. """
    absFilePath = os.path.abspath(name_directory)
    # Check if the last element is a file.py
    fichero = absFilePath.split('/')[-1]
    if fichero.endswith('.py'):
        absFilePath = absFilePath.replace("/" + fichero, "")
    print("This script absolute path is ", absFilePath)
    read_Directory(absFilePath, name_directory)


def read_Directory(absFilePath, repo):
    """ Extract the .py files from the directory. """
    pos = ''
    print('Directory: ')
    path = absFilePath
    try:
        directory = os.listdir(path)
        print(directory)
        for i in range(0, len(directory)):
            if directory[i].endswith('.py'):
                print('Python File: ' + str(directory[i]))
                pos = path + "/" + directory[i]
                read_File(pos, repo)
            elif '.' not in directory[i]:
                print('\nOpening another directory...\n')
                path2 = absFilePath + '/' + directory[i]
                try:
                    read_Directory(path2, directory[i])
                except NotADirectoryError:
                    pass
    except FileNotFoundError:
        pass



def read_File(pos, repo):
    """ Read the file and return the tree. """
    with open(pos) as fp:
        my_code = fp.read()
        try:
            tree = ast.parse(my_code)
            # print (ast.dump(tree))
            iterate_List(tree, pos, repo)
        except SyntaxError:
            print('There is a misspelled code')
            pass

# Initialize a list to store IterTree instances
iter_tree_instances = []

def iterate_List(tree, pos, repo):
    """ Iterate list and assign attributes."""
    for i in range(0, len(SetClass)):
        for j in range(0, len(SetClass[i])):
            attrib = SetClass[i][j]
            obj = deepen(tree, attrib, pos, repo)
            iter_tree_instances.append(obj)


def deepen(tree, attrib, pos, repo):
    """ Create class object """
    file = pos.split('/')[-1]
    return IterTree(tree, attrib, file, repo)

def summary_Levels():
    """ Summarize the analysis. """
    dict_total, dict_summary, dict_repo, dict_unique_total = read_Json()
    result, num_files = show_Results(dict_total, dict_summary, dict_repo, dict_unique_total)
    print(result)

    user_input = input("Do you want more detailed summary (y for yes and n for no): ")
    if user_input.lower() == 'y':
        # Load the JSON data from the file
        with open('data.json', 'r') as file:
            data = json.load(file)

        # Variables to track constructs by level and type
        output = {}

        # Recorremos todos los repositorios y archivos
        for repo_name, files in data.items():
            for file_name, constructs in files.items():
                for construct in constructs:
                    construct_class = construct.get("Class", "").lower()
                    level = construct.get("Level", "")

                    if level not in output:
                        output[level] = {}
                    if construct_class not in output[level]:
                        output[level][construct_class] = 0
                    output[level][construct_class] += 1

        # Sort the levels and constructs
        sorted_levels = sorted(output.items())

        # Print the formatted output
        for level, constructs in sorted_levels:
            print(f"Level {level}:")
            sorted_constructs = sorted(constructs.items(), key=lambda x: x[1], reverse=True)
            for construct_name, count in sorted_constructs:
                print(f"  Construct '{construct_name}': {count}")

        print('=====================================\n')

        result = 0
        for instance in iter_tree_instances:
            result += instance.compute_percentage()

        print("The percentage detected is: ", result / num_files, "%\n")
        print('=====================================\n')

if __name__ == "__main__":
    try:
        type_option = sys.argv[1]
        option = sys.argv[2]
    except:
        sys.exit("Usage: python3 file.py type-option('directory', " +
                 "'repo-url', 'user') option(directory, url, user)")
    choose_option()
    summary_Levels()