import os
import json
import pandas as pd

def compile_to_excel():
    extraction_dir = '.state/extraction'
    output_file = 'master_programs_masterlist.xlsx'
    
    if not os.path.exists(extraction_dir):
        print(f"Directory {extraction_dir} not found. No data to compile.")
        return

    data_rows = []
    
    # Read every JSON file created by the analyzer agents
    for filename in os.listdir(extraction_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(extraction_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Add university and program tags based on filename if missing
                    file_parts = filename.replace('.json', '').split('-')
                    if 'university_id' not in data:
                        data['university_id'] = file_parts[0] if len(file_parts) > 0 else 'Unknown'
                    data_rows.append(data)
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not data_rows:
        print("No valid JSON data found to compile.")
        return

    # Convert to DataFrame and export to Excel
    df = pd.DataFrame(data_rows)
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"✅ Success: Compiled {len(data_rows)} programs into {output_file}")

if __name__ == "__main__":
    compile_to_excel()