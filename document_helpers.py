def dump_item_to_document(item_group: str, item_id: str, item: dict[str, str]):
    """This function converts the abstract representation of an
    item into a single text document for embedding.

    Args:
        item_group (str): The item group of the item, e.g. Weapon.
        item_id (str): The numerical id of the item. This is unique within the item group.
        item (dict[str, str]): The various text fields found in the item.
    """    
    metadata: dict = {'item_type': item_group}
    item_text: str = f'''Data dump from an item the player can find in the game Elden Ring:
==============================
Item Type: {item_group}
--------------------------
'''
    for field_type, text in item.items():
        item_text += f'''{field_type}: {text}'''
        item_text += "\n--------------------------\n"
        metadata[field_type] = text
    item_doc = {'id': (item_group + "_" + item_id), 'metadata':metadata, 'text_to_embed': item_text}
    return item_doc

def add_embeddings(input_docs, embeddings_model):
    embeddings = embeddings_model.embed_documents([doc['text_to_embed'] for doc in input_docs])
    for embedding, doc in zip(embeddings, input_docs):
        doc['values'] = embedding
    return input_docs
