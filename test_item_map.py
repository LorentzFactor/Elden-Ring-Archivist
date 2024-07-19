from item_map import EldenRingItemMap
from langchain_core.documents import Document

item_groups = {
    "Accessory": ["Name", "Caption", "Info"],
    "Arts": ["Name", "Caption"],
    "Gem": ["Name", "Caption", "Effect", "Info"],
    "Goods": ["Name", "Caption", "Effect", "Info", "Info2", "Dialog"],
    "Magic": ["Name", "Caption", "Info"],
    "Protector": ["Name", "Caption", "Info"],
    "Weapon": ["Name", "Caption", "Effect", "Info"]
}
path = "Carian-Archive-main/GameText/GR/data/INTERROOT_win64/msg/engUS/"

item_map = EldenRingItemMap(item_groups, path)


def dump_item_to_document(item_group, item_id, item):
    item_text = f'''Data dump from an item the player can find in the game Elden Ring:
==============================
Item Type: {item_group}
--------------------------
'''
    for field_type, text in item.items():
        item_text += f'''{field_type}: {text}'''
        item_text += "\n--------------------------\n"
    item_doc = Document(item_text, id=(item_group + "_" + item_id))
    return item_doc

simplest_items_as_doc = item_map.dump_items(dump_item_to_document)
