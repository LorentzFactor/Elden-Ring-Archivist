import os
from bs4 import BeautifulSoup
from collections import defaultdict
from typing import Pattern
import re

class EldenRingItemMap:
    not_null: Pattern[str] = r'^(?!.*%null%).*'
    enhanced: Pattern[str] = r'^(?!.*\+\d).*'

    def __init__(self, item_groups: dict[str, list[str]], path: str):
        self._item_groups: dict[str, list[str]] = item_groups
        self.items: dict[str, dict] = {group: defaultdict(dict) for group in self._item_groups.keys()}
        self._path: str = path
        self._blacklist_ids: list[str] = []
        for file_name, file_content in self._load_data_files():
            self.process_file(file_name, file_content)

    def _load_data_files(self):
        '''
        Loads all xml files in the path directory as BeautifulSoup objects.
        Use of yield leaves open the possibility of implementing async loading
        later.
        '''
        for file in os.listdir(self._path):
            if file.endswith(".xml"):
                file_name: str = file.split('.')[0]
                parsed_content = BeautifulSoup(open(self._path + file, 'r'), features='xml')
                yield file_name, parsed_content
    
    def process_file(self, file_name: str, file: BeautifulSoup):
        '''
        Extract all relevant information from a given file
        '''
        group, field = self._determine_item_group_and_field(file_name)
        if group is None:
            return
        for xml_elm in file.find_all(id=True):
            if re.fullmatch(self.not_null, xml_elm.string):
                continue
            self._add_item_text(xml_elm, group, field)

    def _add_item_text(self, text_elm, text_group, text_field):
        item_id = text_elm.get('id')
        # Skip blacklisted items
        if item_id in self._blacklist_ids:
            return
        # Add enhanced item names to blacklist, as these are essentially duplicates
        if text_field == "Name" and re.match(self.enhanced, text_elm.string):
            self._add_item_to_blacklist(item_id, text_group)
        else:
            self.items[text_group][item_id][text_field] = text_elm.string

    def _add_item_to_blacklist(self, item_id, text_group):
        # Add item to blacklist
        self._blacklist_ids.append(item_id)
        # Delete it from items dict if it is already there
        if item_id in self.items[text_group]:
            del self.items[text_group][item_id]

    def _determine_item_group_and_field(self, file_name):
        for group, fields in self._item_groups.items():
            for field in fields:
                if file_name == (group + field) or file_name == field:
                    return group, field
        return None, None

    def dump_items(self, dump_function: callable):
        dumped_items = []
        for group, group_items in self.items.items():
            for item_id, item in group_items.items():
                dumped_value = dump_function(group, item_id, item)
                dumped_items.append(dumped_value)
        return dumped_items
