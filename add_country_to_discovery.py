import os
import json
import re
import sys

sys.path.append('.')
from sync_pipeline_state import find_discovery_file

DISCOVERY_DIR = '.state/discovery'
STATE_FILE = '.state/pipeline-state.md'

discovery_files = [f.replace('.json', '') for f in os.listdir(DISCOVERY_DIR) if f.endswith('.json')]
file_to_country = {}

with open(STATE_FILE, 'r') as f:
    for line in f:
        match = re.match(r'- \[(.)\]\[(.)\] (.+?) \((.+)\)\s*$', line)
        if match:
            uni_name = match.group(3)
            country = match.group(4)
            found_file = find_discovery_file(uni_name, discovery_files)
            if found_file:
                file_to_country[found_file] = country

print(f"Mapped {len(file_to_country)} files to countries.")

updated = 0
for filename in os.listdir(DISCOVERY_DIR):
    if not filename.endswith('.json'):
        continue
    file_base = filename.replace('.json', '')
    country = file_to_country.get(file_base, 'Unknown')
    
    filepath = os.path.join(DISCOVERY_DIR, filename)
    with open(filepath, 'r') as f:
        programs = json.load(f)
        
    modified = False
    for p in programs:
        if p.get('country') != country:
            p['country'] = country
            modified = True
            
    if modified:
        with open(filepath, 'w') as f:
            json.dump(programs, f, indent=2)
        updated += 1

print(f"Updated {updated} discovery files with country field.")
