import os
from bs4 import BeautifulSoup
from collections import defaultdict
import re

def load_data_files(path):  
    '''Loads all files in the path directory'''
    files = {}
    for file in os.listdir(path):
        if file.endswith(".xml"):
            files[file.split('.')[0]] = BeautifulSoup(open(path + file, 'r'), features='xml')
            
    return files


class EldenRingItemMap:
    not_null = r'^(?!.*%null%).*'
    enhanced = r'^(?!.*\+\d).*'
    item_groups = {
        "Accessory": ["Name", "Caption", "Info"],
        "Arts": ["Name", "Caption"],
        "Gem": ["Name", "Caption", "Effect", "Info"],
        "Goods": ["Name", "Caption", "Effect", "Info", "Info2", "Dialog"],
        "Magic": ["Name", "Caption", "Info"],
        "Protector": ["Name", "Caption", "Info"],
        "Weapon": ["Name", "Caption", "Effect", "Info"]
    }

    def __init__(self):
        self.items = {group: defaultdict(dict) for group in self.item_groups.keys()}
        self._blacklist_ids = []

    def _add_item_text(self, text_elm, text_group, text_field):
        item_id = text_elm.get('id')
        if item_id in self._blacklist_ids:
            return

        # Skip enhanced item names, as these are essentially duplicates
        if text_field == "Name" and re.match(self.enhanced, text_elm.string):
            self._blacklist_ids.append(item_id)
            try:
                del self.items[text_group][item_id]
            except KeyError:
                pass
            return
        self.items[text_group][item_id][text_field] = text_elm.string

    def _determine_item_group_and_field(self, file_name):
        for group, fields in self.item_groups.items():
            for field in fields:
                if file_name == (group + field) or file_name == field:
                    return group, field
        return None, None

    def process_file(self, file_name, file):
        group, field = self._determine_item_group_and_field(file_name)
        if group is None:
            return
        for xml_elm in file.find_all(id=True):
            if re.fullmatch(self.not_null, xml_elm.string):
                continue
            self._add_item_text(xml_elm, group, field)
