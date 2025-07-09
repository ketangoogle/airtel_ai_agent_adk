from google.cloud import bigquery
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import os

# --- Configuration ---
GCP_PROJECT_ID = "ketan-gcp-playground"
BIGQUERY_DATASET = "airtel_support_agent"

# Construct full table IDs
FAQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.FAQ_Knowledgebase"
SOP_TABLE_ID = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.SOP_Knowledgebase"

# --- Initialization ---
# Initialize the BigQuery client and the semantic search model
# This code will run once when the module is imported.
try:
    client = bigquery.Client(project=GCP_PROJECT_ID)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("BigQuery Knowledge Base: Initialized BigQuery client and Sentence Transformer model.")
except Exception as e:
    print(f"Error initializing BigQuery Knowledge Base: {e}")
    client = None
    model = None

def fetch_data_from_bigquery(table_id):
    """Helper function to fetch all data from a BigQuery table."""
    try:
        query = f"SELECT * FROM `{table_id}`"
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        return pd.DataFrame() # Return empty dataframe on error

def search_knowledge_base(user_query: str) -> dict:
    """
    Performs a semantic search against the FAQ and SOP tables in BigQuery.

    This is the main function the knowledge_agent will use as its tool.
    """
    if not client or not model:
        return {"error": "Knowledge base is not initialized."}

    # 1. Fetch the latest data from BigQuery
    faq_df = fetch_data_from_bigquery(FAQ_TABLE_ID)
    sop_df = fetch_data_from_bigquery(SOP_TABLE_ID)

    # 2. Perform semantic search on FAQs first
    if not faq_df.empty:
        corpus = faq_df['question'].dropna().tolist()
        query_embedding = model.encode(user_query, convert_to_tensor=True)
        corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        best_match_idx = torch.argmax(cos_scores).item()

        if cos_scores[best_match_idx] > 0.65: # Confidence threshold
            return {"source": "FAQ", "result": faq_df.iloc[best_match_idx].to_dict()}

    # 3. If no relevant FAQ, search SOPs
    if not sop_df.empty:
        corpus = sop_df['problem_description'].dropna().tolist()
        query_embedding = model.encode(user_query, convert_to_tensor=True)
        corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        best_match_idx = torch.argmax(cos_scores).item()

        if cos_scores[best_match_idx] > 0.65: # Confidence threshold
            return {"source": "SOP", "result": sop_df.iloc[best_match_idx].to_dict()}

    return {"source": "None", "result": "No relevant information found in the knowledge base."}