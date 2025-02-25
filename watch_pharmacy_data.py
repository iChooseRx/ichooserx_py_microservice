import os
import time
import pandas as pd
import psycopg2
import logging
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🔹 Configure logging settings
logging.basicConfig(
    filename="pharmacy_updates.log",  # Log file name
    level=logging.INFO,               # Log only INFO level and above
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format log entries
    datefmt="%Y-%m-%d %H:%M:%S"        # Date format
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
os.makedirs(WATCHED_DIR, exist_ok=True) # Ensure directory exists

class PharmacyDataHandler(FileSystemEventHandler):
    """ Watches for changes in the pharmacy_data directory and processes updated files. """
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".csv", ".xlsx", ".json")):
            print(f"\n📌 Detected file update: {event.src_path}")
            process_file(event.src_path)

def process_file(file_path):
    """Reads and processes a pharmacy inventory file and updates the database."""
    # ✅ Log script start
    logging.info("🚀 Pharmacy inventory watch script started!")
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path) # Ignores comment lines, blank lines skipped
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            print("❌ Unsupported file format. Skipping.")
            return
        
        print(f"\n📂 Processing file: {file_path}")
        print(df.head()) # Display sample data for 
        
        # ✅ Log detected file processing
        logging.info(f"📂 Processing file: {file_path}")

        # ✅ Remove duplicate rows
        df = df.drop_duplicates(subset=["Pharmacy", "NDC"])

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        for _, row in df.iterrows():
            if "Pharmacy" in df.columns and "NDC" in df.columns and "Drug" in df.columns:
                if pd.isnull(row["Pharmacy"]) or pd.isnull(row["NDC"]) or pd.isnull(row["Drug"]):
                    print(f"⚠️ Skipping row due to missing required fields: {row}")
                    continue

                pharmacy_name = row["Pharmacy"].strip()
                ndc = row["NDC"].strip()
                drug_name = row["Drug"].strip()
                stock_status = row.get("Stock", "Unknown")
                form = row.get("Form", None)
                strength = row.get("Strength", None)
                supplier = row.get("Supplier", None)

                # 🔍 Check if pharmacy exists
                cursor.execute("SELECT id FROM pharmacies WHERE name = %s LIMIT 1;", (pharmacy_name,))
                pharmacy_id = cursor.fetchone()

                if not pharmacy_id:
                    print(f"🔹 Pharmacy '{pharmacy_name}' not found. Creating it now...")
                    default_address = "Unknown Address"
                    default_phone = "000-000-0000"

                    cursor.execute("""
                        INSERT INTO pharmacies (name, address, phone, created_at, updated_at)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        ON CONFLICT (name) DO UPDATE 
                        SET updated_at = NOW()
                        RETURNING id;
                    """, (pharmacy_name, default_address, default_phone))
                    pharmacy_id = cursor.fetchone()
                    print(f"✅ Successfully created or updated pharmacy: {pharmacy_name}")

                if pharmacy_id:
                    pharmacy_id = pharmacy_id[0]

                    # 🔍 Check if the NDC already exists for this pharmacy
                    cursor.execute("""
                        SELECT id, drug_name, stock_status, form, strength, supplier 
                        FROM pharmacy_inventories 
                        WHERE pharmacy_id = %s AND ndc = %s LIMIT 1;
                    """, (pharmacy_id, ndc))
                    
                    existing_record = cursor.fetchone()

                    if existing_record:
                        record_id, db_drug_name, db_stock_status, db_form, db_strength, db_supplier = existing_record

                        # Convert `None` to empty strings for accurate comparison
                        db_values = (db_drug_name or "", db_stock_status or "", db_form or "", db_strength or "", db_supplier or "")
                        new_values = (drug_name or "", stock_status or "", form or "", strength or "", supplier or "")

                        if db_values != new_values:  # Only update if something actually changed
                            print(f"🔍 Attempting UPDATE for {pharmacy_name} - {ndc}: {db_values} → {new_values}")

                            cursor.execute("""
                                UPDATE pharmacy_inventories 
                                SET drug_name = %s, stock_status = %s, form = %s, strength = %s, supplier = %s, last_updated = NOW()
                                WHERE id = %s;
                            """, (drug_name, stock_status, form, strength, supplier, record_id))

                            conn.commit()  # ✅ PostgreSQL commits the update
                             # ✅ Log update to file
                            logging.info(f"UPDATED {pharmacy_name} - {ndc}: {db_values} → {new_values}")

                            print(f"✅ Successfully UPDATED {pharmacy_name} - {ndc} in the database.")
                        else:
                            print(f"✅ No changes detected for {pharmacy_name} - {ndc}, skipping update.")
                    else:
                        # ✅ Insert new record if no existing entry is found
                        cursor.execute("""
                            INSERT INTO pharmacy_inventories 
                            (pharmacy_id, ndc, drug_name, stock_status, form, strength, supplier, last_updated, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW());
                        """, (pharmacy_id, ndc, drug_name, stock_status, form, strength, supplier))
                        print(f"✅ Inserted new inventory for {pharmacy_name} - {ndc}")
                        # log new inserts
                        logging.info(f"INSERTED {pharmacy_name} - {ndc} with values: {new_values}")
                    conn.commit()

        print("\n✅ File processing complete!\n")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

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
        observer.stop()
    observer.join()
