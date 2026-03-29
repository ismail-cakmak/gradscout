#!/usr/bin/env python3
"""Sync pipeline-state.md with actual discovery and extraction files."""

import os
import json
import re

DISCOVERY_DIR = '.state/discovery'
EXTRACTION_DIR = '.state/extraction'
STATE_FILE = '.state/pipeline-state.md'

# Manual mapping for special cases
UNI_NAME_MAP = {
    'charité - universitätsmedizin berlin': 'charite-universitatsmedizin-berlin',
    'charite - universitatsmedizin berlin': 'charite-universitatsmedizin-berlin',
    'university of tübingen': 'university-of-tubingen',
    'university of tubingen': 'university-of-tubingen',
    'university of göttingen': 'university-of-gottingen',
    'university of gottingen': 'university-of-gottingen',
    'university of würzburg': 'university-of-wurzburg',
    'university of wurzburg': 'university-of-wurzburg',
    'university of münster': 'university-of-munster',
    'university of munster': 'university-of-munster',
    'école polytechnique': 'ecolepolytechnique',
    'ecole polytechnique': 'ecolepolytechnique',
    'karolinska institute': 'karolinskainstitutet',
    'technical university of munich': 'technical-university-of-munich',
    'lmu munich': 'lmu-munich',
    'heidelberg university': 'heidelberg-university',
    'humboldt university of berlin': 'humboldt-university-of-berlin',
    'rwth aachen university': 'rwth-aachen-university',
    'university of bonn': 'university-of-bonn',
    'free university of berlin': 'free-university-of-berlin',
    'university of hamburg': 'university-of-hamburg',
    'university of freiburg': 'university-of-freiburg',
    'technical university of berlin': 'technical-university-of-berlin',
    'university of cologne': 'university-of-cologne',
    'karlsruhe institute of technology': 'karlsruhe-institute-of-technology',
    'tu dresden': 'tu-dresden',
    'delft university of technology': 'delft-university-of-technology',
    'university of amsterdam': 'university-of-amsterdam',
    'wageningen university': 'wageningen-university',
    'leiden university': 'leiden-university',
    'university of groningen': 'university-of-groningen',
    'erasmus university rotterdam': 'erasmus-university-rotterdam',
    'maastricht university': 'maastricht-university',
    'radboud university': 'radboud-university',
    'vrije universiteit amsterdam': 'vrije-universiteit-amsterdam',
    'university of twente': 'university-of-twente',
    'eindhoven university of technology': 'eindhoven-university-of-technology',
    'university of oxford': 'university-of-oxford',
    'university of cambridge': 'university-of-cambridge',
    'imperial college london': 'imperial-college-london',
    'ucl': 'ucl',
    'university of edinburgh': 'universityofedinburgh',
    "king's college london": 'kings-college-london',
    'university of manchester': 'university-of-manchester',
    'lse': 'lse',
    'university of bristol': 'universityofbristol',
    'university of warwick': 'universityofwarwick',
    'psl university': 'psluniversity',
    'sorbonne university': 'sorbonneuniversity',
    'paris-saclay university': 'parissaclayuniversity',
    'trinity college dublin': 'trinitycollegedublin',
    'university college dublin': 'universitycollegedublin',
    'uppsala university': 'uppsalauniversity',
    'lund university': 'lunduniversity',
    'kth royal institute of technology': 'kthroyalinstituteoftechnology',
    'stockholm university': 'stockholmuniversity',
    'eth zurich': 'ethzurich',
    'epfl': 'epfl',
    'university of zurich': 'universityofzurich',
    'university of helsinki': 'universityofhelsinki',
    'aalto university': 'aaltouniversity',
    'university of copenhagen': 'universityofcopenhagen',
    'technical university of denmark': 'technicaluniversityofdenmark',
    'aarhus university': 'aarhusuniversity',
}

def normalize_name(name):
    """Normalize a name for matching."""
    name = name.lower().strip()
    # Remove special characters but keep basic structure
    name = re.sub(r'[^\w\s-]', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    name = ' '.join(name.split())  # Normalize whitespace
    return name

def find_discovery_file(uni_name, discovery_files):
    """Find matching discovery file for a university name."""
    uni_norm = normalize_name(uni_name)

    # First try direct mapping
    if uni_name.lower() in UNI_NAME_MAP:
        mapped = UNI_NAME_MAP[uni_name.lower()]
        if mapped in discovery_files:
            return mapped

    # Try normalized match
    for disc in discovery_files:
        disc_norm = normalize_name(disc.replace('-', ' '))
        if uni_norm == disc_norm:
            return disc

    # Try contains match
    for disc in discovery_files:
        disc_norm = normalize_name(disc.replace('-', ' '))
        if uni_norm in disc_norm or disc_norm in uni_norm:
            return disc

    # Try word-based matching
    uni_words = set(uni_norm.split())
    for disc in discovery_files:
        disc_norm = normalize_name(disc.replace('-', ' '))
        disc_words = set(disc_norm.split())
        # Check for significant overlap
        common = uni_words & disc_words
        if len(common) >= 2 and len(common) / max(len(uni_words), len(disc_words)) > 0.5:
            return disc

    return None

def main():
    # Get all discovery files and their status
    discovery_files = [f.replace('.json', '') for f in os.listdir(DISCOVERY_DIR) if f.endswith('.json')]

    uni_status = {}
    for filename in os.listdir(DISCOVERY_DIR):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(DISCOVERY_DIR, filename)
        with open(filepath, 'r') as f:
            programs = json.load(f)
        done = sum(1 for p in programs if p.get('status') in ('done', 'failed'))
        pending = sum(1 for p in programs if p.get('status') == 'pending')
        uni_status[filename.replace('.json', '')] = (done, pending)

    # Read and update state file
    with open(STATE_FILE, 'r') as f:
        lines = f.readlines()

    new_lines = []
    in_universities = False
    matched_count = 0
    unmatched_unis = []

    for line in lines:
        if '## Universities' in line:
            in_universities = True
            new_lines.append(line)
            continue

        if in_universities and line.startswith('- ['):
            match = re.match(r'- \[(.)\]\[(.)\] (.+?) \((.+)\)\s*$', line)
            if match:
                uni_name = match.group(3)
                country = match.group(4)

                # Find matching discovery file
                matched_file = find_discovery_file(uni_name, discovery_files)

                if matched_file and matched_file in uni_status:
                    disc_done, disc_pending = uni_status[matched_file]
                    disc_box = 'x'
                    ext_box = 'x' if disc_pending == 0 and disc_done > 0 else ' '
                    matched_count += 1
                else:
                    disc_box = ' '
                    ext_box = ' '
                    unmatched_unis.append(uni_name)

                new_lines.append(f'- [{disc_box}][{ext_box}] {uni_name} ({country})\n')
                continue

        if in_universities and line.startswith('## '):
            in_universities = False

        new_lines.append(line)

    with open(STATE_FILE, 'w') as f:
        f.writelines(new_lines)

    # Print summary
    print(f"Matched {matched_count} universities")
    if unmatched_unis:
        print(f"Unmatched: {unmatched_unis}")

    print("\n=== Status Summary ===")
    print("\nUniversities with ALL programs extracted:")
    for disc_name, (done, pending) in sorted(uni_status.items()):
        if pending == 0 and done > 0:
            print(f"  [x][x] {disc_name} ({done} programs)")

    print("\nUniversities with PARTIAL extraction:")
    for disc_name, (done, pending) in sorted(uni_status.items()):
        if pending > 0 and done > 0:
            print(f"  [x][ ] {disc_name} ({done} done, {pending} pending)")

    print("\nUniversities with NO extraction yet:")
    for disc_name, (done, pending) in sorted(uni_status.items()):
        if pending > 0 and done == 0:
            print(f"  [x][ ] {disc_name} ({pending} pending)")

    total_done = sum(d for d, p in uni_status.values())
    total_pending = sum(p for d, p in uni_status.values())
    print(f"\nTotal: {total_done} done, {total_pending} pending")

if __name__ == "__main__":
    main()
