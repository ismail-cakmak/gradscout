#!/usr/bin/env python3
"""
Filter discovery and extraction files for business/management programs.
Creates separate folders with only business-related programs.
"""

import os
import json
import re
import shutil

DISCOVERY_DIR = '.state/discovery'
EXTRACTION_DIR = '.state/extraction'
DISCOVERY_BUSINESS_DIR = '.state/discovery-business'
EXTRACTION_BUSINESS_DIR = '.state/extraction-business'

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
NON_BUSINESS_KEYWORDS = [
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
    'informatics', 'informatics', 'hci', 'human computer', 'interaction design',
    'game', 'media informatics', 'network', 'cloud computing', 'distributed systems',
    'algorithm', 'computational', 'quantum', 'statistics', 'econometrics'
]

# Additional technical keywords to catch more programs
TECH_KEYWORDS = [
    'cs', 'ai', 'ml', 'dl', 'nlp', 'cv', 'iot', 'api', 'sql', 'nosql',
    'web', 'mobile', 'app', 'system', 'computing', 'programming', 'coding',
    'automation', 'control', 'signal processing', 'image processing', 'vision',
    'autonomous', 'smart', 'intelligent system', 'knowledge', 'semantic',
    'graph', 'database', 'information system', 'telecommunication', '5g',
    'blockchain', 'crypto', 'virtual', 'augmented', 'xr', 'vr', 'ar'
]


def is_business_program(program_name, program_url=''):
    """
    Determine if a program is business/management related.
    Returns True if business, False if technical/other.
    """
    name_lower = program_name.lower()
    url_lower = program_url.lower() if program_url else ''
    combined = name_lower + ' ' + url_lower

    # First check for strong technical indicators
    tech_score = 0
    for keyword in TECH_KEYWORDS + NON_BUSINESS_KEYWORDS:
        if keyword in combined:
            tech_score += 1

    # Check for business keywords
    business_score = 0
    for keyword in BUSINESS_KEYWORDS:
        if keyword in combined:
            business_score += 1

    # If more technical keywords match, it's likely technical
    if tech_score > business_score:
        return False

    # If business keywords match and tech score is low, it's business
    if business_score > 0 and tech_score <= 1:
        return True

    # Edge cases - check specific patterns
    # Management + technical = still consider business-adjacent
    if ('management' in combined or 'innovation' in combined) and tech_score >= 1:
        return True

    # Pure technical programs
    if any(x in name_lower for x in ['computer science', 'software', 'data science', 'ai ', 'ml ', 'robotics']):
        return False

    return False


def filter_discovery_files():
    """Filter discovery files and create business versions."""
    print("=" * 60)
    print("FILTERING DISCOVERY FILES")
    print("=" * 60)

    total_programs = 0
    business_programs = 0

    for filename in os.listdir(DISCOVERY_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(DISCOVERY_DIR, filename)
        with open(filepath, 'r') as f:
            programs = json.load(f)

        # Filter for business programs
        business_progs = []
        for prog in programs:
            total_programs += 1
            prog_name = prog.get('program_name', '')
            prog_url = prog.get('url', '')

            if is_business_program(prog_name, prog_url):
                business_progs.append(prog)
                business_programs += 1

        # Save business programs if any found
        if business_progs:
            business_filepath = os.path.join(DISCOVERY_BUSINESS_DIR, filename)
            with open(business_filepath, 'w') as f:
                json.dump(business_progs, f, indent=2)
            print(f"{filename}: {len(business_progs)} business programs")
        else:
            # Create empty file to track that we processed it
            uni_name = filename.replace('.json', '')
            # Check if any program had business keywords at all
            with open(filepath, 'r') as f:
                all_progs = json.load(f)

            # List all programs for manual review
            print(f"{filename}: 0 business programs (all technical)")

    print(f"\nDiscovery: {business_programs}/{total_programs} programs are business-related")
    return business_programs, total_programs


def filter_extraction_files():
    """Filter extraction files and copy business ones to business folder."""
    print("\n" + "=" * 60)
    print("FILTERING EXTRACTION FILES")
    print("=" * 60)

    business_files = 0

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

        if is_business_program(prog_name_display, ''):
            # Copy to business folder
            src = os.path.join(EXTRACTION_DIR, filename)
            dst = os.path.join(EXTRACTION_BUSINESS_DIR, filename)
            shutil.copy(src, dst)
            business_files += 1
            print(f"Copied: {filename}")

    print(f"\nExtraction: {business_files} files are business-related")
    return business_files


def create_summary():
    """Create a summary of what was filtered."""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    # Count discovery business files
    disc_files = [f for f in os.listdir(DISCOVERY_BUSINESS_DIR) if f.endswith('.json')]

    # Count extraction business files
    extr_files = [f for f in os.listdir(EXTRACTION_BUSINESS_DIR) if f.endswith('.json')]

    print(f"\nBusiness Discovery Files: {len(disc_files)}")
    for f in sorted(disc_files):
        filepath = os.path.join(DISCOVERY_BUSINESS_DIR, f)
        with open(filepath, 'r') as file:
            progs = json.load(file)
        print(f"  {f}: {len(progs)} programs")

    print(f"\nBusiness Extraction Files: {len(extr_files)}")
    for f in sorted(extr_files)[:20]:  # Show first 20
        print(f"  {f}")
    if len(extr_files) > 20:
        print(f"  ... and {len(extr_files) - 20} more")


def main():
    # Ensure output directories exist
    os.makedirs(DISCOVERY_BUSINESS_DIR, exist_ok=True)
    os.makedirs(EXTRACTION_BUSINESS_DIR, exist_ok=True)

    # Filter files
    disc_business, disc_total = filter_discovery_files()
    extr_business = filter_extraction_files()

    # Create summary
    create_summary()

    print("\n" + "=" * 60)
    print("OUTPUT LOCATIONS:")
    print(f"  Business Discovery: {DISCOVERY_BUSINESS_DIR}/")
    print(f"  Business Extraction: {EXTRACTION_BUSINESS_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
