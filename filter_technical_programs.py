#!/usr/bin/env python3
"""
Create technical-only versions of discovery and extraction files.
These are the programs that are NOT business/management related.
"""

import os
import json
import re
import shutil

DISCOVERY_DIR = '.state/discovery'
EXTRACTION_DIR = '.state/extraction'
DISCOVERY_TECH_DIR = '.state/discovery-technical'
EXTRACTION_TECH_DIR = '.state/extraction-technical'

# Business/Management keywords for filtering
BUSINESS_KEYWORDS = [
    'business', 'management', 'admin', 'commerce', 'entrepreneur', 'innovation',
    'finance', 'accounting', 'marketing', 'leadership', 'strategy', 'organizational',
    'human resource', 'hr ', 'supply chain', 'logistics', 'operations', 'project management',
    'international business', 'mba', 'executive', 'consulting', 'governance',
    'retail', 'hospitality', 'tourism', 'real estate', 'banking', 'investment',
    'economic', 'trade', 'corporate', 'sustainability', 'venture'
]

# Keywords that indicate NON-business programs (technical/STEM)
TECH_KEYWORDS = [
    'computer science', 'software engineering', 'data science', 'machine learning',
    'artificial intelligence', 'cybersecurity', 'robotics', 'embedded', 'electrical',
    'mechanical', 'civil engineering', 'chemical engineering', 'physics', 'mathematics',
    'biology', 'bioinformatics', 'medicine', 'health', 'clinical', 'pharmacy',
    'chemistry', 'materials', 'aerospace', 'automotive', 'energy engineering',
    'geoscience', 'environmental science', 'ecology', 'zoology', 'botany',
    'linguistics', 'literature', 'history', 'philosophy', 'sociology', 'anthropology',
    'psychology', 'neuroscience', 'cognitive', 'education', 'teaching', 'pedagogy',
    'law', 'legal', 'jurisprudence', 'theology', 'religious', 'arts', 'music',
    'design', 'architecture', 'urban planning', 'geography', 'archaeology',
    'informatics', 'hci', 'human computer', 'interaction design',
    'game', 'media informatics', 'network', 'cloud computing', 'distributed systems',
    'algorithm', 'computational', 'quantum', 'statistics', 'econometrics',
    'cs', 'ai', 'ml', 'dl', 'nlp', 'cv', 'iot', 'api', 'sql', 'nosql',
    'web', 'mobile', 'app', 'system', 'computing', 'programming', 'coding',
    'automation', 'control', 'signal processing', 'image processing', 'vision',
    'autonomous', 'smart', 'intelligent system', 'knowledge', 'semantic',
    'graph', 'database', 'information system', 'telecommunication', '5g',
    'blockchain', 'crypto', 'virtual', 'augmented', 'xr', 'vr', 'ar'
]


def is_technical_program(program_name, program_url=''):
    """
    Determine if a program is technical (NOT business/management).
    Returns True if technical, False if business/other.
    """
    name_lower = program_name.lower()
    url_lower = program_url.lower() if program_url else ''
    combined = name_lower + ' ' + url_lower

    # Check for business keywords first
    business_score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword in combined:
            business_score += 1

    # Check for technical keywords
    tech_score = 0
    for keyword in TECH_KEYWORDS:
        if keyword in combined:
            tech_score += 1

    # If technical keywords match, it's technical
    if tech_score > 0:
        return True

    # If business keywords match and no tech keywords, it's business (not technical)
    if business_score > 0:
        return False

    # Default to technical for STEM-adjacent fields
    # (science, engineering, math, etc. without business keywords)
    stem_indicators = ['science', 'engineering', 'technology', 'studies', 'programme']
    if any(x in combined for x in stem_indicators):
        return True

    return True  # Default to technical if unclear


def filter_discovery_files():
    """Filter discovery files and create technical versions."""
    print("=" * 60)
    print("FILTERING DISCOVERY FILES (TECHNICAL)")
    print("=" * 60)

    total_programs = 0
    technical_programs = 0

    for filename in os.listdir(DISCOVERY_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(DISCOVERY_DIR, filename)
        with open(filepath, 'r') as f:
            programs = json.load(f)

        # Filter for technical programs
        technical_progs = []
        for prog in programs:
            total_programs += 1
            prog_name = prog.get('program_name', '')
            prog_url = prog.get('url', '')

            if is_technical_program(prog_name, prog_url):
                technical_progs.append(prog)
                technical_programs += 1

        # Save technical programs if any found
        if technical_progs:
            technical_filepath = os.path.join(DISCOVERY_TECH_DIR, filename)
            with open(technical_filepath, 'w') as f:
                json.dump(technical_progs, f, indent=2)
            print(f"{filename}: {len(technical_progs)} technical programs")
        else:
            print(f"{filename}: 0 technical programs (all business)")

    print(f"\nDiscovery: {technical_programs}/{total_programs} programs are technical")
    return technical_programs, total_programs


def filter_extraction_files():
    """Filter extraction files and copy technical ones to technical folder."""
    print("\n" + "=" * 60)
    print("FILTERING EXTRACTION FILES (TECHNICAL)")
    print("=" * 60)

    technical_files = 0

    for filename in os.listdir(EXTRACTION_DIR):
        if not filename.endswith('.json'):
            continue

        # Parse filename: universityname-programname.json
        if '-' not in filename:
            continue

        base = filename[:-5]  # Remove .json
        parts = base.split('-', 1)
        if len(parts) != 2:
            continue

        uni_name, prog_name = parts
        prog_name_display = prog_name.replace('-', ' ')

        if is_technical_program(prog_name_display, ''):
            # Copy to technical folder
            src = os.path.join(EXTRACTION_DIR, filename)
            dst = os.path.join(EXTRACTION_TECH_DIR, filename)
            shutil.copy(src, dst)
            technical_files += 1
            print(f"Copied: {filename}")

    print(f"\nExtraction: {technical_files} files are technical")
    return technical_files


def create_summary():
    """Create a summary of what was filtered."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Count discovery technical files
    disc_files = [f for f in os.listdir(DISCOVERY_TECH_DIR) if f.endswith('.json')]

    # Count extraction technical files
    extr_files = [f for f in os.listdir(EXTRACTION_TECH_DIR) if f.endswith('.json')]

    print(f"\nTechnical Discovery Files: {len(disc_files)}")
    for f in sorted(disc_files):
        filepath = os.path.join(DISCOVERY_TECH_DIR, f)
        with open(filepath, 'r') as file:
            progs = json.load(file)
        print(f"  {f}: {len(progs)} programs")

    print(f"\nTechnical Extraction Files: {len(extr_files)}")
    for f in sorted(extr_files)[:30]:  # Show first 30
        print(f"  {f}")
    if len(extr_files) > 30:
        print(f"  ... and {len(extr_files) - 30} more")


def main():
    # Ensure output directories exist
    os.makedirs(DISCOVERY_TECH_DIR, exist_ok=True)
    os.makedirs(EXTRACTION_TECH_DIR, exist_ok=True)

    # Filter files
    disc_tech, disc_total = filter_discovery_files()
    extr_tech = filter_extraction_files()

    # Create summary
    create_summary()

    print("\n" + "=" * 60)
    print("OUTPUT LOCATIONS:")
    print(f"  Technical Discovery: {DISCOVERY_TECH_DIR}/")
    print(f"  Technical Extraction: {EXTRACTION_TECH_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
