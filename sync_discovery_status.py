#!/usr/bin/env python3
import os
import json

base_dir = '/home/ismailcakmak/Desktop/DEV/master-search'
discovery_dir = os.path.join(base_dir, '.state/discovery')
extraction_dir = os.path.join(base_dir, '.state/extraction')

def normalize_url(url):
    if not url:
        return ""
    url = url.lower().strip()
    if url.endswith('/'):
        url = url[:-1]
    url = url.replace('https://', '').replace('http://', '').replace('www.', '')
    return url

extracted_urls = set()
extracted_names = set()

# Load all extracted programs
for filename in os.listdir(extraction_dir):
    if not filename.endswith('.json'):
        continue
    
    filepath = os.path.join(extraction_dir, filename)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            url = data.get('program_url')
            name = data.get('program_name')
            if url:
                extracted_urls.add(normalize_url(url))
            if name:
                extracted_names.add(name.lower().strip())
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print(f"Loaded {len(extracted_urls)} unique URLs and {len(extracted_names)} unique names from extractions.")

# Process discovery files
total_programs = 0
total_done = 0
total_pending = 0

for filename in os.listdir(discovery_dir):
    if not filename.endswith('.json'):
        continue
        
    filepath = os.path.join(discovery_dir, filename)
    try:
        with open(filepath, 'r') as f:
            programs = json.load(f)
            
        modified = False
        for prog in programs:
            total_programs += 1
            url = prog.get('url')
            name = prog.get('program_name')
            norm_url = normalize_url(url)
            
            # Check if extracted
            is_extracted = False
            if norm_url and norm_url in extracted_urls:
                is_extracted = True
            elif name and name.lower().strip() in extracted_names:
                is_extracted = True
                
            new_status = "done" if is_extracted else "pending"
            
            if prog.get('status') != new_status:
                prog['status'] = new_status
                modified = True
                
            if new_status == "done":
                total_done += 1
            else:
                total_pending += 1
                
        if modified:
            with open(filepath, 'w') as f:
                json.dump(programs, f, indent=2)
                
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(f"Sync complete. Total programs: {total_programs}, Done: {total_done}, Pending: {total_pending}")
