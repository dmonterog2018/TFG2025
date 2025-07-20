"""
CLASS PROGRAM TO ITERATE ON THE TREE
"""

import ast
import csv
import json
import levels


class IterTree():
    """Class to iterate tree."""

    def __init__(self, tree, attrib, file, repo):
        """Class constructor."""
        self.tree = tree
        self.attrib = attrib
        self.name = file
        self.repo = repo
        self.total_constructs = 0
        self.detected_constructs = 0
        self.myDataCsv = [['Repository',
                           'File Name',
                           'Class',
                           'Start Line',
                           'End Line',
                           'Displacement',
                           'Level']]
        self.myDataJson = {}
        self.locate_Tree()

    def locate_Tree(self):
        """Method iterating on the tree."""
        for self.node in ast.walk(self.tree):
            if type(self.node) == eval(self.attrib):
                self.detected_constructs += 1
                self.level = ''
                self.clase = ''
                levels.levels(self)
                self.assign_List()
                self.assign_Dict()
        self.total_constructs = len(list(ast.walk(self.tree)))
        self.write_FileCsv()
        self.write_FileJson()

    def assign_List(self):
        """Create object list."""
        if hasattr(self.node, 'lineno') and hasattr(self.node, 'end_lineno') and hasattr(self.node, 'col_offset'):
            if self.clase != '' and self.level != '':
                self.list = [self.repo, self.name, self.clase, self.node.lineno,
                             self.node.end_lineno, self.node.col_offset,
                             self.level]
                self.myDataCsv.append(self.list)

    def assign_Dict(self):
        """Create object dictionary."""
        if hasattr(self.node, 'lineno') and hasattr(self.node, 'end_lineno') and hasattr(self.node, 'col_offset'):
            if self.clase != '' and self.level != '':
                if self.repo not in self.myDataJson:
                    self.myDataJson[self.repo] = {}
                if self.name not in self.myDataJson[self.repo]:
                    self.myDataJson[self.repo][self.name] = []
                self.myDataJson[self.repo][self.name].append({
                    'Class': str(self.clase),
                    'Start Line': str(self.node.lineno),
                    'End Line': str(self.node.end_lineno),
                    'Displacement': str(self.node.col_offset),
                    'Level': str(self.level)
                })

    def write_FileCsv(self):
        """Write the collected data into the CSV file."""
        with open('data.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.myDataCsv)

    def write_FileJson(self):
        """Merge and write the collected data into the JSON file."""
        import os

        existing_data = {}
        if os.path.exists('data.json'):
            with open('data.json', 'r', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}

        for repo, files in self.myDataJson.items():
            if repo not in existing_data:
                existing_data[repo] = {}
            for file_name, constructs in files.items():
                if file_name not in existing_data[repo]:
                    existing_data[repo][file_name] = []
                existing_data[repo][file_name].extend(constructs)

        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, indent=4)

    def compute_percentage(self):
        """Compute the percentage of detected constructs."""
        if self.total_constructs > 0:
            self.percentage_detected = (self.detected_constructs / self.total_constructs) * 100
        else:
            self.percentage_detected = 0
        return self.percentage_detected
