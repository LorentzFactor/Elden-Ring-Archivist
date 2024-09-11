from langchain_openai import OpenAIEmbeddings
from item_map import EldenRingItemMap
from pinecone import Pinecone
import os
from itertools import batched
from document_helpers import dump_raw_text_no_cut_content, add_embeddings

# Define the fields we wish to collect for each item type
item_groups = {
    "Accessory": ["Name", "Caption", "Info"],
    "Arts": ["Name", "Caption"],
    "Gem": ["Name", "Caption", "Effect", "Info"],
    "Goods": ["Name", "Caption", "Effect", "Info", "Info2", "Dialog"],
    "Magic": ["Name", "Caption", "Info"],
    "Protector": ["Name", "Caption", "Info"],
    "Weapon": ["Name", "Caption", "Effect", "Info"]
}
# Path to (English) data dump
path = "Carian-Archive-main/GameText/GR/data/INTERROOT_win64/msg/engUS/"

# Initialize db
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)

# Initialize embedding model
embeddings_model = OpenAIEmbeddings(model='text-embedding-3-large')

# Constructing an EldenRingItemMap parses all .xml files in path for item data
item_map = EldenRingItemMap(item_groups, path)

# Dump it, apply embedding model
items_as_doc = item_map.dump_items(dump_raw_text_no_cut_content)
items_as_doc = add_embeddings(items_as_doc, embeddings_model)

# Generate upsert commands for embeddings, including metadata
# Note that we don't actually add the document itself! Just the data we used to generate it, and its embedding.
db_commands = []
for item in items_as_doc:
    command = item.copy()
    del command['text_to_embed']
    db_commands.append(command)

# Our index has already been created via Pinecone's website - we just need to add our docs
index = pc.Index('elden-ring-default-index')
for batch in batched(db_commands, 100):
    index.upsert(batch, 'raw_text_no_cut_content')
