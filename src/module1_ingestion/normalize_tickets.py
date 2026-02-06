import pandas as pd
import re
import os

# --- CONFIGURATION & PATHS ---
# We use absolute paths so this script runs correctly from anywhere
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# INPUT: We read from the RAW folder (Original Data)
INPUT_FILE = os.path.join(CURRENT_DIR, '../../data/raw/customer_support_tickets.csv')

# OUTPUT: We save to the PROCESSED folder (Clean Data)
# Note: This is a CSV, not JSON. Module 2 creates the JSON.
OUTPUT_FILE = os.path.join(CURRENT_DIR, '../../data/processed/cleaned_support_tickets.csv')

def clean_text(text):
    if not isinstance(text, str):
        return "no description provided"
    text = text.lower()
    # BUG FIX: Replace special chars with a SPACE (' '), not empty string ('')
    text = re.sub(r'[^a-z0-9\s]', ' ', text) 
    # Remove double spaces created by the replacement
    text = " ".join(text.split())
    return text

def run_pipeline():
    print(f"Loading raw data from: {INPUT_FILE}...")
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("❌ Error: Could not find 'customer_support_data.csv' in 'data/raw/'.")
        print("Please check your file structure.")
        return

    # 1. Standardize Column Headers (snake_case)
    df.columns = [col.lower().replace(' ', '_').strip() for col in df.columns]
    print(f"Columns normalized: {df.columns.tolist()}")

    # 2. Fix 'ticket_status' (The NaN Fix)
    # First, fill strictly missing values with 'Open'
    df['ticket_status'] = df['ticket_status'].fillna('Open')
    
    # Normalize casing (Open vs open vs OPEN)
    df['ticket_status'] = df['ticket_status'].str.title()
    
    # Define the Master Map
    status_map = {
        'Pending': 'OPEN',
        'Open': 'OPEN',
        'Processing': 'OPEN',
        'On Hold': 'OPEN',
        'Resolved': 'CLOSED',
        'Closed': 'CLOSED',
        'Completed': 'CLOSED'
    }
    
    # Apply map. logic: If value is in map, use it. If not, default to 'OPEN'.
    df['ticket_status'] = df['ticket_status'].map(status_map).fillna('OPEN')

    # 3. Clean the Description Text
    # Handle missing descriptions first
    df['ticket_description'] = df['ticket_description'].fillna("no description provided")
    df['ticket_description'] = df['ticket_description'].apply(clean_text)

    # 4. Handle NaN values for the rest of the file
    # (Replaces NaN with None/Empty string so JSON doesn't break later)
    df = df.where(pd.notnull(df), None)

    # 5. Save to CSV
    # Ensure the directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    
    print("\n--- STATUS COUNTS (Verification) ---")
    print(df['ticket_status'].value_counts())
    print(f"\n✅ Success! Cleaned data saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_pipeline()