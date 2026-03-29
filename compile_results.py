import os
import json
import pandas as pd

def normalize_url(url):
    if not url:
        return ""
    url = url.lower().strip()
    if url.endswith('/'):
        url = url[:-1]
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    return url

def compile_to_excel():
    discovery_dir = '.state/discovery'
    extraction_dir = '.state/extraction'
    output_file = 'master_programs_masterlist.xlsx'
    
    if not os.path.exists(discovery_dir):
        print(f"Directory {discovery_dir} not found. No data to compile.")
        return

    # Load all extracted data into a dictionary indexed by normalized URL
    extracted_by_url = {}
    extracted_by_name = {}
    
    if os.path.exists(extraction_dir):
        for filename in os.listdir(extraction_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(extraction_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        url = normalize_url(data.get('program_url', ''))
                        name = (data.get('program_name') or "").lower().strip()
                        
                        file_parts = filename.replace('.json', '').split('-')
                        if 'university_id' not in data:
                            data['university_id'] = file_parts[0] if len(file_parts) > 0 else 'Unknown'
                            
                        if url:
                            extracted_by_url[url] = data
                        if name:
                            extracted_by_name[name] = data
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

    data_rows = []
    
    # Iterate over all discovery files to include every program
    for filename in sorted(os.listdir(discovery_dir)):
        if not filename.endswith('.json'):
            continue
            
        uni_id = filename.replace('.json', '')
        filepath = os.path.join(discovery_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                programs = json.load(f)
                
            for prog in programs:
                prog_url = normalize_url(prog.get('url', ''))
                prog_name = (prog.get('program_name') or "").lower().strip()
                
                # Check for extraction
                ext_data = extracted_by_url.get(prog_url) or extracted_by_name.get(prog_name)
                
                # Build the row
                row = {
                    'country': prog.get('country', 'Unknown'),
                    'university_id': uni_id,
                    'program_name': prog.get('program_name'),
                    'discovery_url': prog.get('url'),
                    'status': prog.get('status', 'pending')
                }
                
                # Merge in extraction data if available
                if ext_data:
                    for k, v in ext_data.items():
                        # Do not override base keys and rename program_url
                        if k not in ['university_id', 'program_name', 'status', 'country'] and k != 'program_url':
                            row[k] = v
                    
                data_rows.append(row)
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    if not data_rows:
        print("No valid JSON data found to compile.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(data_rows)
    
    # Export to Excel with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Group by country
        for country, group in df.groupby('country'):
            # Sheet names in Excel cannot be longer than 31 characters
            sheet_name = str(country)[:31]
            # Replace invalid characters if necessary (Excel does not allow: \ / ? * [ ] :)
            for bad_char in ['\\', '/', '?', '*', '[', ']', ':']:
                sheet_name = sheet_name.replace(bad_char, '')
                
            group.to_excel(writer, sheet_name=sheet_name, index=False)
            
    print(f"✅ Success: Compiled {len(data_rows)} target programs comprehensively into {output_file} across multiple sheets.")

if __name__ == "__main__":
    compile_to_excel()