from google.cloud import bigquery
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import os
from dotenv import load_dotenv
load_dotenv()

GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")

FAQ_TABLE_ID = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.FAQ_Knowledgebase"
SOP_TABLE_ID = f"{GCP_PROJECT_ID}.{BIGQUERY_DATASET}.SOP_Knowledgebase"

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
    if not client:
        return pd.DataFrame()
    try:
        query = f"SELECT * FROM `{table_id}`"
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"Error fetching data from {table_id}: {e}")
        return pd.DataFrame()

def search_knowledge_base(user_query: str) -> dict:
    """
    Searches a knowledge base of FAQs and Standard Operating Procedures (SOPs) to find solutions for a user's problem.

    Use this tool whenever a user asks a question, describes a problem, or is looking for help.
    It performs a semantic search to find the most relevant document to answer the query.
    
    Args:
        user_query: The user's question or problem description.
    
    Returns:
        A dictionary containing the source ('FAQ' or 'SOP') and the result, or a message if no information is found.
    """
    if not client or not model:
        return {"error": "Knowledge base is not initialized."}

    # 1. Fetch the latest data from BigQuery
    faq_df = fetch_data_from_bigquery(FAQ_TABLE_ID)
    sop_df = fetch_data_from_bigquery(SOP_TABLE_ID)

    # 2. Perform semantic search on FAQs first
    if not faq_df.empty and 'question' in faq_df.columns:
        corpus_faq = faq_df['question'].dropna().tolist()
        if corpus_faq:
            query_embedding = model.encode(user_query, convert_to_tensor=True)
            corpus_embeddings = model.encode(corpus_faq, convert_to_tensor=True)
            cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
            best_match_idx = int(torch.argmax(cos_scores).item())

            if cos_scores[best_match_idx] > 0.65: # Confidence threshold
                return {"source": "FAQ", "result": faq_df.iloc[best_match_idx].to_dict()}

    # 3. If no relevant FAQ, search SOPs
    if not sop_df.empty and 'problem_description' in sop_df.columns:
        corpus_sop = sop_df['problem_description'].dropna().tolist()
        if corpus_sop:
            query_embedding = model.encode(user_query, convert_to_tensor=True)
            corpus_embeddings = model.encode(corpus_sop, convert_to_tensor=True)
            cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
            best_match_idx = int(torch.argmax(cos_scores).item())

            if cos_scores[best_match_idx] > 0.65: # Confidence threshold
                return {"source": "SOP", "result": sop_df.iloc[best_match_idx].to_dict()}

    return {"source": "None", "result": "No relevant information was found in the knowledge base."}