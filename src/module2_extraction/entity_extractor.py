import pandas as pd
import json
import os
import time
import re
import math
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm
from dotenv import load_dotenv

# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(CURRENT_DIR, '../../data/processed/cleaned_support_tickets.csv')
OUTPUT_FILE = os.path.join(CURRENT_DIR, '../../data/processed/extracted_triples.json')

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_json_from_text(text):
    """Extracts JSON object from text using Regex."""
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except:
        return None

def clean_nans(data_list):
    """
    Recursively looks for NaN in a list of dicts
    and replaces them with None (which becomes 'null' in JSON).
    """
    cleaned_list = []
    for item in data_list:
        clean_item = {}
        for key, value in item.items():
            # Check if value is float and is NaN
            if isinstance(value, float) and math.isnan(value):
                clean_item[key] = None
            else:
                clean_item[key] = value
        cleaned_list.append(clean_item)
    return cleaned_list

def extract_triples(df):
    try:
        llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        return []

    template = """
    Analyze this support ticket description: "{text}"
    
    Return ONLY a valid JSON object with these keys:
    {{
      "issue_summary": "Brief technical summary (max 5 words)",
      "root_cause": "The likely technical cause (Hardware/Software/Network/User)",
      "sentiment": "Positive/Neutral/Negative"
    }}
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    chain = prompt | llm

    results = []
    
    print(f"--- Starting Extraction on {len(df)} tickets ---")
    
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            # 1. Run AI Extraction
            response = chain.invoke({"text": row['ticket_description']})
            
            # 2. Extract JSON safely
            ai_data = extract_json_from_text(response.content)
            
            if not ai_data:
                # If AI fails, provide default empty values so we don't break the schema
                ai_data = {
                    "issue_summary": "Processing Failed", 
                    "root_cause": "Unknown", 
                    "sentiment": "Neutral"
                }
            
            # 3. Hybrid Merge
            combined_record = row.to_dict()
            combined_record.update(ai_data)
            results.append(combined_record)
            
            time.sleep(1.5) # Be nice to the API
            
        except Exception as e:
            results.append(row.to_dict())

    return results

if __name__ == "__main__":
    try:
        # 1. Load Data
        df = pd.read_csv(INPUT_FILE)
        
        # Limit for testing
        #remove this line if you want to exarct all the triples from the csv
        df = df.head(100) 
        
        print(f"Data Loaded. Processing {len(df)} rows...")
        
        # 2. Extract
        triples = extract_triples(df)
        
        # 3. THE FIX: Clean NaNs right before saving
        final_clean_data = clean_nans(triples)
        
        # 4. Save Results
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(final_clean_data, f, indent=4)
            
        print(f"\n✅ Success! Processed {len(final_clean_data)} records.")
        print(f"Saved to: {OUTPUT_FILE}")
        
    except FileNotFoundError:
        print("Error: Input file not found. Run Module 1 first!")