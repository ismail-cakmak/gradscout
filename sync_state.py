#!/usr/bin/env python3
"""Sync discovery program status with actual extraction files - improved matching."""

import os
import json
import re

DISCOVERY_DIR = ".state/discovery"
EXTRACTION_DIR = ".state/extraction"
STATE_FILE = ".state/pipeline-state.md"

def get_extraction_files():
    """Get dict mapping university -> set of program name fragments."""
    extraction_map = {}
    if not os.path.exists(EXTRACTION_DIR):
        return extraction_map

    for f in os.listdir(EXTRACTION_DIR):
        if not f.endswith('.json'):
            continue
        # Filename format: universityname-programname.json
        if '-' in f:
            parts = f[:-5].split('-', 1)  # Split on first hyphen
            if len(parts) == 2:
                uni, prog = parts
                if uni not in extraction_map:
                    extraction_map[uni] = set()
                extraction_map[uni].add(prog)
    return extraction_map

def normalize_for_matching(name):
    """Normalize name for fuzzy matching."""
    name = name.lower().strip()
    # Remove common suffixes
    name = re.sub(r'\s+(msc|ma|bsc|ba|masters?|degree|program)', '', name)
    # Replace hyphens and spaces
    name = re.sub(r'[-\s]+', '', name)
    return name

def program_matches_extraction(program_name, prog_fragments):
    """Check if program name matches any extraction file fragment."""
    normalized_prog = normalize_for_matching(program_name)

    for fragment in prog_fragments:
        normalized_frag = normalize_for_matching(fragment.replace('-', ' '))
        # Check if one contains the other or they're similar
        if normalized_prog in normalized_frag or normalized_frag in normalized_prog:
            return True
        # Check for significant overlap
        if len(normalized_prog) > 4 and len(normalized_frag) > 4:
            # Simple similarity check
            if normalized_prog == normalized_frag:
                return True
    return False

def sync_discovery_file(filepath, extraction_map):
    """Sync a discovery file and return (programs, pending_count, done_count)."""
    with open(filepath, 'r') as f:
        programs = json.load(f)

    filename = os.path.basename(filepath).replace('.json', '')
    uni_fragments = extraction_map.get(filename, set())

    pending_count = 0
    done_count = 0

    for program in programs:
        program_name = program.get('program_name', '')

        if program_matches_extraction(program_name, uni_fragments):
            program['status'] = 'done'
            done_count += 1
        else:
            program['status'] = 'pending'
            pending_count += 1

    return programs, pending_count, done_count

def update_pipeline_state():
    """Update pipeline-state.md checkboxes based on discovery files."""
    with open(STATE_FILE, 'r') as f:
        lines = f.readlines()

    extraction_map = get_extraction_files()
    new_lines = []
    in_universities = False

    for line in lines:
        if '## Universities' in line:
            in_universities = True
            new_lines.append(line)
            continue

        if in_universities and line.startswith('- ['):
            match = re.match(r'- \[(.)\]\[(.)\] (.+?) \((.+)\)\s*$', line)
            if match:
                discovery_checked = match.group(1)
                extraction_checked = match.group(2)
                uni_name = match.group(3)
                country = match.group(4)

                # Normalize university name for filename
                uni_filename = re.sub(r'[^a-z0-9]', '', uni_name.lower()).replace(' ', '')
                # Handle special cases
                uni_filename = uni_filename.replace('université', 'universite')
                uni_filename = uni_filename.replace('écol', 'ecol')
                uni_filename = uni_filename.replace('tübingen', 'tubingen')
                uni_filename = uni_filename.replace('gottingen', 'gottingen')

                discovery_path = os.path.join(DISCOVERY_DIR, f"{uni_filename}.json")

                if os.path.exists(discovery_path):
                    with open(discovery_path, 'r') as f:
                        programs = json.load(f)

                    pending = sum(1 for p in programs if p.get('status') == 'pending')
                    done = sum(1 for p in programs if p.get('status') == 'done')
                    failed = sum(1 for p in programs if p.get('status') == 'failed')

                    # Discovery is done if file exists and has programs
                    if len(programs) > 0:
                        discovery_checked = 'x'

                    # Extraction is done if all programs are done or failed
                    if pending == 0 and (done > 0 or failed > 0):
                        extraction_checked = 'x'
                    else:
                        extraction_checked = ' '
                else:
                    # Try alternate filename patterns
                    for alt_name in os.listdir(DISCOVERY_DIR):
                        if alt_name.endswith('.json') and uni_name.lower() in alt_name.replace('.json', '').replace('-', ' '):
                            discovery_path = os.path.join(DISCOVERY_DIR, alt_name)
                            with open(discovery_path, 'r') as f:
                                programs = json.load(f)
                            pending = sum(1 for p in programs if p.get('status') == 'pending')
                            done = sum(1 for p in programs if p.get('status') == 'done')
                            if len(programs) > 0:
                                discovery_checked = 'x'
                            if pending == 0 and done > 0:
                                extraction_checked = 'x'
                            break

                new_lines.append(f"- [{discovery_checked}][{extraction_checked}] {uni_name} ({country})\n")
                continue

        if in_universities and line.startswith('## '):
            in_universities = False

        new_lines.append(line)

    with open(STATE_FILE, 'w') as f:
        f.writelines(new_lines)

def main():
    extraction_map = get_extraction_files()
    print(f"Found extraction files for {len(extraction_map)} universities")

    total_pending = 0
    total_done = 0

    for filename in sorted(os.listdir(DISCOVERY_DIR)):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(DISCOVERY_DIR, filename)
        try:
            programs, pending, done = sync_discovery_file(filepath, extraction_map)

            # Write back updated discovery file
            with open(filepath, 'w') as f:
                json.dump(programs, f, indent=2)

            if pending + done > 0:
                status = "ALL DONE" if pending == 0 and done > 0 else f"{done} done, {pending} pending"
                print(f"{filename}: {status}")
                total_done += done
                total_pending += pending
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"\nTotal: {total_done} done, {total_pending} pending")

    # Update pipeline state
    update_pipeline_state()
    print("\nUpdated pipeline-state.md")

if __name__ == "__main__":
    main()
