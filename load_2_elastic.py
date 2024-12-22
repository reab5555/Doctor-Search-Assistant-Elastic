import pandas as pd
import ast
from elasticsearch import Elasticsearch
from tqdm import tqdm

# Initialize Elasticsearch client
client = Elasticsearch(
    "host:port",
    basic_auth=("username", "password")
)

# Define the index name
index_name = "doctors_il_db"

# Delete the index if it exists
if client.indices.exists(index=index_name):
    client.indices.delete(index=index_name)
    print(f"Index '{index_name}' deleted.")

# Create new index
client.indices.create(
    index=index_name,
    body={
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "first_name": {"type": "text"},
                "last_name": {"type": "text"},
                "license_number": {"type": "keyword"},
                "title": {"type": "text"},
                "specialty": {"type": "text"},
                "subspecialty": {"type": "text"},
                "phone_numbers": {"type": "keyword"},
                "city": {"type": "text"},
                "street": {"type": "text"},
                "house_number": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384
                }
            }
        }
    }
)
print(f"Index '{index_name}' created successfully.")

def parse_phones(phones_str):
    if pd.isna(phones_str):
        return []
    try:
        phones = ast.literal_eval(phones_str)
        return phones
    except Exception as e:
        print(f"Error parsing phones: {e}")
        return []

def generate_embedding(client, model_id, text):
    try:
        response = client.ml.infer_trained_model(
            model_id=model_id,
            docs=[{"text_field": text}],
            inference_config={"text_embedding": {}}
        )
        return response['inference_results'][0]['predicted_value']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Define the model ID
model_id = ".multilingual-e5-small"

# Load the dataset
file_path = 'ServiceBook.xlsx'
data = pd.read_excel(file_path, sheet_name='Sheet1')

# Process each document individually
for idx, row in tqdm(data.iterrows(), total=len(data), desc="Processing Documents"):
    # Build the full address
    street = row['רחוב'] if pd.notna(row['רחוב']) else ''
    house_number = str(row['מספר בית']) if pd.notna(row['מספר בית']) else ''
    street_address = f"{street} {house_number}".strip()

    # Create the text for embedding
    first_name = row['שם פרטי'] if pd.notna(row['שם פרטי']) else ''
    last_name = row['שם משפחה'] if pd.notna(row['שם משפחה']) else ''
    title = row['תואר'] if pd.notna(row['תואר']) else ''
    specialty = row['התמחות'] if pd.notna(row['התמחות']) else ''
    subspecialty = row['תת-התמחות'] if pd.notna(row['תת-התמחות']) else ''
    city = row['עיר'] if pd.notna(row['עיר']) else ''

    embedding_text = f"{first_name} {last_name} {title} {specialty} {subspecialty} {city} {street_address}"

    # Generate embedding
    embedding = generate_embedding(client, model_id, embedding_text)

    if embedding is None:
        print(f"Skipping document due to embedding generation failure for text: {embedding_text}")
        continue

    # Build the document
    document = {
        "first_name": first_name if first_name else None,
        "last_name": last_name if last_name else None,
        "license_number": str(row['מספר רשיון']) if pd.notna(row['מספר רשיון']) else None,
        "title": title if title else None,
        "specialty": specialty if specialty else None,
        "subspecialty": subspecialty if subspecialty else None,
        "phone_numbers": parse_phones(row['טלפונים']),
        "city": city if city else None,
        "street": street if street else None,
        "house_number": house_number if house_number else None,
        "embedding": embedding
    }

    # Index the document without specifying an ID
    try:
        response = client.index(index=index_name, document=document)
        if not response['_id']:
            print(f"Warning: No ID generated for document {idx}")
    except Exception as e:
        print(f"Error indexing document {idx}: {e}")

print("Indexing completed. Refreshing index...")
client.indices.refresh(index=index_name)

# Verify indexing
count = client.count(index=index_name)
print(f"Total documents indexed: {count['count']}")