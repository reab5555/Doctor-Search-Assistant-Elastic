from elasticsearch import Elasticsearch

# Initialize Elasticsearch client
client = Elasticsearch(
    "host:port",
    basic_auth=("username", "password")
)

# Function to generate embeddings for a query
def generate_embedding(client, model_id, query_text):
    try:
        response = client.ml.infer_trained_model(
            model_id=model_id,
            docs=[{"text_field": query_text}],
            inference_config={"text_embedding": {}}
        )
        return response["inference_results"][0]["predicted_value"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Function to perform semantic search
def semantic_search(client, index_name, query_embedding, top_n=5):
    """
    Perform semantic search using cosine similarity.
    """
    try:
        response = client.search(
            index=index_name,
            query={
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            },
            size=top_n
        )

        hits = response['hits']['hits']
        if not hits:
            print("No results found. Please verify embeddings and query compatibility.")
        else:
            print("\nSearch Results:")
            for hit in hits:
                source = hit['_source']
                print(f"\nScore: {hit['_score']:.2f}")
                print(f"Name: {source.get('title', '')} {source.get('first_name', '')} {source.get('last_name', '')}")
                print(f"Specialty: {source.get('specialty', '')}")
                if source.get('subspecialty'):
                    print(f"Subspecialty: {source['subspecialty']}")
                print(f"Location: {source.get('street', '')} {source.get('house_number', '')}, {source.get('city', '')}")
                if source.get('phone_numbers'):
                    print(f"Phone numbers: {', '.join(source['phone_numbers'])}")
    except Exception as e:
        print(f"Error during semantic search: {e}")

if __name__ == "__main__":
    # Define the model ID (ensure the model is available in your cluster)
    model_id = ".multilingual-e5-small"

    # Example query text (in Hebrew): "Find an eye doctor in Tel Aviv"
    query_text = "תמצא רופא עיניים מבאר שבע"

    # Generate embedding for the query
    query_embedding = generate_embedding(client, model_id, query_text)
    if query_embedding:
        index_name = "doctors_il_db"
        semantic_search(client, index_name, query_embedding, top_n=5)
    else:
        print("Failed to generate query embedding.")