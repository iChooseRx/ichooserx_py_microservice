import os
import time
import re
import pandas as pd
import psycopg2
import logging
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from thefuzz import fuzz
import traceback

# 🔹 Configure logging settings
logging.basicConfig(
    filename="pharmacy_updates.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Directory to watch for new pharmacy files
WATCHED_DIR = "pharmacy_data"
os.makedirs(WATCHED_DIR, exist_ok=True)  # Ensure directory exists

# 🔹 Column name standardization
COLUMN_SYNONYMS = {
    "Pharmacy": ["pharmacy", "pharmacy name", "pharmacy_name", "store"],
    "NDC": ["ndc", "national drug code", "ndc code"],
    "Drug": ["drug", "drug name", "drug_name", "medication"],
    "Stock": ["stock", "inventory", "stock status", "stock_status", "availability"],
    "Form": ["form", "dosage form", "type"],
    "Strength": ["strength", "dosage strength", "concentration"],
    "Supplier": ["supplier", "manufacturer", "company"]
}

def extract_pharmacy_name(file_path):
    """Extracts the pharmacy name from filenames like 'b&b_pharmacy_ndc_list'."""
    filename = os.path.basename(file_path)  # Get the file name only (no path)
    filename_no_ext = os.path.splitext(filename)[0]  # Remove extension

    # Extract everything before "_pharmacy_ndc_list"
    match = re.search(r"^(.*?)_pharmacy_ndc_list", filename_no_ext, re.IGNORECASE)

    if match:
        # Convert underscores to spaces, keep special characters (like "&"), and title-case the name
        return match.group(1).replace("_", " ").title()
    else:
        return None  # Return None if no match
    
# ✅ Fuzzy Matching Function
def fuzzy_match_column(col, synonyms_dict, threshold=80):
    """Returns the standardized column name if a fuzzy match is found."""
    best_match = None
    best_score = 0

    for canonical, synonyms in synonyms_dict.items():
        for s in synonyms:
            score = fuzz.ratio(col.lower(), s.lower())
            if score > best_score:
                best_score = score
                best_match = canonical

    return best_match if best_score >= threshold else None

# ✅ Normalize Column Names
def normalize_column_names(df, synonyms_dict):
    """Renames columns in `df` to standardized names if they match any synonyms or fuzzy matches."""
    lookup = {}

    # Create a mapping from possible column names (lowercased) to canonical names
    for canonical, synonyms in synonyms_dict.items():
        for s in synonyms:
            lookup[s.lower()] = canonical

    rename_map = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in lookup:
            rename_map[col] = lookup[key]
        else:
            fuzzy_match = fuzzy_match_column(col, synonyms_dict)
            if fuzzy_match:
                rename_map[col] = fuzzy_match
            else:
                rename_map[col] = col  # Keep column unchanged if no match found

    df.rename(columns=rename_map, inplace=True)
    return df

# ✅ Watchdog Handler for New File Changes
class PharmacyDataHandler(FileSystemEventHandler):
    """Watches for changes in the pharmacy_data directory and processes updated files."""
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".csv", ".xlsx", ".json")):
            print(f"\n📌 Detected file update: {event.src_path}")
            process_file(event.src_path)

# Store the last processed timestamp
last_processed = {}

# ✅ Process File Function
def process_file(file_path, user_id):
    """Reads and processes a pharmacy inventory file and updates the database."""
    logging.info(f"🚀 Processing file {file_path} for user {user_id}")

    try:
        # ✅ Load Data into Pandas DataFrame
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, encoding="utf-8")
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            print(f"❌ Unsupported file format. Skipping: {file_path}")
            return

        print(f"\n📂 Processing file: {file_path}")

        # ✅ Normalize Column Names
        df = normalize_column_names(df, COLUMN_SYNONYMS)

        # ✅ Ensure Required Columns Are Present
        required_cols = {"NDC"}
        if not required_cols.issubset(df.columns):
            logging.warning(f"❌ Missing required columns: {required_cols - set(df.columns)} in {file_path}. Skipping.")
            return

        # ✅ Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # 🔍 Find Pharmacy Associated with User ID
        cursor.execute("SELECT id, name FROM pharmacies WHERE user_id = %s LIMIT 1;", (user_id,))
        pharmacy_data = cursor.fetchone()

        if not pharmacy_data:
            print(f"❌ No pharmacy found for user {user_id}. Skipping file.")
            return

        pharmacy_id, pharmacy_name = pharmacy_data
        print(f"✅ Found pharmacy '{pharmacy_name}' for user {user_id}")

        # ✅ Assign the pharmacy name to all rows
        df["Pharmacy"] = pharmacy_name

        # ✅ Remove duplicate rows based on Pharmacy + NDC
        df = df.drop_duplicates(subset=["Pharmacy", "NDC"])

        for _, row in df.iterrows():
            ndc = row["NDC"].strip()
            drug_name = row.get("Drug", "Unknown Drug").strip()
            stock_status = row.get("Stock", "Unknown")
            form = row.get("Form", None) or ""
            strength = row.get("Strength", None) or ""
            supplier = row.get("Supplier", None) or ""

            # 🔍 Check if the NDC already exists for this pharmacy
            cursor.execute("""
                SELECT id FROM pharmacy_inventories 
                WHERE pharmacy_id = %s AND ndc = %s LIMIT 1;
            """, (pharmacy_id, ndc))

            existing_record = cursor.fetchone()

            if existing_record:
                record_id = existing_record[0]
                cursor.execute("""
                    UPDATE pharmacy_inventories 
                    SET drug_name = %s, stock_status = %s, form = %s, strength = %s, supplier = %s, last_updated = NOW()
                    WHERE id = %s;
                """, (drug_name, stock_status, form, strength, supplier, record_id))
            else:
                cursor.execute("""
                    INSERT INTO pharmacy_inventories 
                    (pharmacy_id, ndc, drug_name, stock_status, form, strength, supplier, last_updated, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW());
                """, (pharmacy_id, ndc, drug_name, stock_status, form, strength, supplier))

        conn.commit()
        cursor.close()
        conn.close()

        print("\n✅ File processing complete!")

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        traceback.print_exc()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    event_handler = PharmacyDataHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCHED_DIR, recursive=False)

    print(f"👀 Watching directory: {WATCHED_DIR} for changes...")
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        observer.stop()
        observer.join()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.error(f"❌ Unexpected error: {e}")
        observer.stop()
        observer.join()
