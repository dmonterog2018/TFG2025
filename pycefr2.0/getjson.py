import json
import os
import re
import configparser
from collections import defaultdict

def extract_Levels(data):
    """ Extract repository levels and classes. """
    dict_total = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    dict_summary = defaultdict(lambda: defaultdict(int))
    dict_repo = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    dict_unique_total = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for repo in data.keys():
        for file, items in data[repo].items():
            unique_levels = set()
            unique_classes = set()
            for item in items:
                level = item.get('Level', '')
                clase = re.sub(r"\s?\d", "", item.get('Class', ''))
                
                if 'Levels' not in dict_total[repo][file]:
                    dict_total[repo][file]['Levels'] = defaultdict(int)
                if 'Classes' not in dict_total[repo][file]:
                    dict_total[repo][file]['Classes'] = defaultdict(int)
                
                dict_total[repo][file]['Levels'][level] += 1
                dict_total[repo][file]['Classes'][clase] += 1
                
                if level:
                    dict_summary['Levels'][level] += 1
                    unique_levels.add(level)
                if clase:
                    dict_summary['Classes'][clase] += 1
                    unique_classes.add(clase)
                
                if 'Levels' not in dict_repo[repo][file]:
                    dict_repo[repo][file]['Levels'] = defaultdict(int)
                dict_repo[repo][file]['Levels'][level] += 1
                
                if 'Classes' not in dict_repo[repo][file]:
                    dict_repo[repo][file]['Classes'] = defaultdict(int)
                dict_repo[repo][file]['Classes'][clase] += 1

            # Track unique occurrences
            for level in unique_levels:
                if 'Levels' not in dict_unique_total[repo][file]:
                    dict_unique_total[repo][file]['Levels'] = defaultdict(int)
                dict_unique_total[repo][file]['Levels'][level] += 1
                
            for class_name in unique_classes:
                if 'Classes' not in dict_unique_total[repo][file]:
                    dict_unique_total[repo][file]['Classes'] = defaultdict(int)
                dict_unique_total[repo][file]['Classes'][class_name] += 1

    return dict_total, dict_summary, dict_repo, dict_unique_total

def write_Results(repo, dict_total, dict_unique_total, dict_summary, dict_repo):
    """ Create .json files with summaries of results. """
    wd = os.getcwd()
    try:
        os.mkdir(wd + "/DATA_JSON")
    except FileExistsError:
        pass

    # Write normal results
    name_file = f"{wd}/DATA_JSON/{repo}.json"
    with open(name_file, 'w') as file:
        json.dump({repo: dict_total[repo]}, file, indent=4)

    # Write unique occurrence results
    unique_name_file = f"{wd}/DATA_JSON/{repo}_unique.json"
    with open(unique_name_file, 'w') as file:
        json.dump({repo: dict_unique_total[repo]}, file, indent=4)

    # Write total data
    total_name_file = f"{wd}/DATA_JSON/total_data.json"
    with open(total_name_file, 'w') as file:
        json.dump(dict_total, file, indent=4)

    # Write summary data
    summary_name_file = f"{wd}/DATA_JSON/summary_data.json"
    with open(summary_name_file, 'w') as file:
        json.dump(dict_summary, file, indent=4)

    # Write repo data
    repo_name_file = f"{wd}/DATA_JSON/repo_data.json"
    with open(repo_name_file, 'w') as file:
        json.dump(dict_repo, file, indent=4)
        
def show_Results(dict_total, dict_summary, dict_repo, dict_unique_total):
    """ Return the result of the analysis. """
    result = '=====================================\nRESULT OF THE ANALYSIS:\n'

    num_files = sum(len(files) for files in dict_total.values())
    result += f'Analyzed .py files: {num_files}\n'
    
    result += '=====================================\n'
    
    levels = sorted(dict_summary['Levels'].items())
    for level, count in levels:
        result += f'Elements of level {level}: {count}\n'

    result += '=====================================\n'

    """# Assuming dict_summary and configuration file paths
    # Initialize dict_result_unique and dict_total
    dict_result_unique = {
        'Levels': defaultdict(int),
        'Classes': defaultdict(lambda: defaultdict(int))
    }
    dict_total = {}  # Replace with actual data loading

    # Load configuration file to map classes to levels
    config = configparser.ConfigParser()
    config.read('configuration_vanilla.cfg')

    # Initialize result container
    result_unique = defaultdict(int)

    # Iterate over sorted classes
    classes = sorted(dict_summary['Classes'].items())
    for clase, count in classes:
        print("\nclase: ", clase)
        # Check if clase exists in config sections
        mapped_level = None
        for section in config.sections():
            if clase == section:
                mapped_level = option
                break
            # Split the section keys to check each class within the section
            for option in config.options(section):
                string = option + " " + section
                string2 = "'" + option + "' " + section
                if clase.lower() == string.lower():
                    mapped_level = option.keys()
                    break
                elif clase.lower() == string2.lower():
                    mapped_level = option
                    break

        if mapped_level:
            result_unique[mapped_level] += count
        else:
            print(f"Level not found for class: {clase}")

    # Display or process result_unique as needed
    for level, count in result_unique.items():
        print(f"Classes of level {level}:")
        for clase, clase_count in dict_result_unique['Classes'][level].items():
            print(f"  - {clase}: {clase_count}")
        print(f"Total classes of level {level}: {count}")"""

    """classes = sorted(dict_summary['Classes'].items())
    for clase, count in classes:
        result += f'Classes {clase}: {count}\n'

    result += '====================================='"""
    return result, num_files

def read_Json():
    """ Read json file. """
    with open('data.json') as file:
        data = json.load(file)
        dict_total, dict_summary, dict_repo, dict_unique_total = extract_Levels(data)
        return dict_total, dict_summary, dict_repo, dict_unique_total

if __name__ == "__main__":
    result = read_Json()
    print(result)
