<img src="icon.png" width="100" alt="alt text">

# Elasticsearch Doctor Query and Index Prototype (Hebrew Version)

This prototype demonstrates a data pipeline and search system for processing and indexing doctor-related data from spreadsheets into Elasticsearch. It supports semantic search and question answering through embedding-based retrieval methods.

## Overview

The system is composed of two primary scripts. The first script, `load_2_elastic.py`, loads data from a spreadsheet, processes it, and creates an Elasticsearch index. The second script, `elastic_search_query.py`, enables querying the indexed data using natural language. This modular design allows for seamless data ingestion and retrieval, focusing on indexing information about doctors.

## Data Processing and Indexing

Data is ingested from an Excel spreadsheet (`ServiceBook.xlsx`) containing doctor information such as names, specialties, contact details, and locations. The script processes each entry, generating embeddings for semantic similarity using the `multilingual-e5-small` model. These embeddings enable advanced search capabilities by storing them as dense vectors in the Elasticsearch index.

The index, named `doctors_il_db`, is created with predefined mappings to accommodate the data schema. Each record is enriched with its corresponding embedding, which is later used during query-time search for precise matching.

## Semantic Search Capabilities

The search functionality enables users to retrieve information through natural language queries. Queries are converted into embeddings using the same model, ensuring compatibility with the indexed data. The system then employs cosine similarity to identify and rank results by relevance. Users can search for specific doctors, specialties, or locations, and the system responds with detailed information about the matches.

For example, querying "Find an eye doctor in Tel Aviv" or "תמצא לי רופא עיניים בתל אביב" will return a list of relevant doctors in Tel Aviv with their specialties and contact information.

## Installation and Setup

To use the system, clone the repository and install the required Python dependencies. Configure the scripts by providing Elasticsearch host details and authentication. Ensure the Elasticsearch cluster is running and has the `multilingual-e5-small` model loaded for embedding generation. Run the `load_2_elastic.py` script to index the data, and use `elastic_search_query.py` to perform searches.

## Future Development

This prototype serves as a foundation for a more comprehensive system. Future improvements may include support for additional models, advanced query parsing, and a user-friendly web interface. Enhancing error handling and robustness will further refine the user experience.

## Conclusion

This project showcases the potential of combining spreadsheet data processing, embedding generation, and Elasticsearch to build a powerful semantic search system. With its focus on doctor-related data, it provides an efficient solution for managing and retrieving critical information. The modular design ensures adaptability for various use cases and datasets, making it a versatile tool for similar applications.
