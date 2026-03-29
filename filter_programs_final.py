#!/usr/bin/env python3
"""
Filter discovery and extraction files into business vs technical (mutually exclusive).
"""

import os
import json
import re
import shutil

DISCOVERY_DIR = '.state/discovery'
EXTRACTION_DIR = '.state/extraction'
DISCOVERY_BUSINESS_DIR = '.state/discovery-business'
DISCOVERY_TECH_DIR = '.state/discovery-technical'
EXTRACTION_BUSINESS_DIR = '.state/extraction-business'
EXTRACTION_TECH_DIR = '.state/extraction-technical'

# Business/Management keywords
BUSINESS_KEYWORDS = [
    'business', 'management', 'admin', 'commerce', 'entrepreneur',
    'finance', 'accounting', 'marketing', 'leadership', 'strategy', 'organizational',
    'human resource', 'hr ', 'supply chain', 'logistics', 'operations', 'project management',
    'international business', 'mba', 'executive', 'consulting', 'governance',
    'retail', 'hospitality', 'tourism', 'real estate', 'banking', 'investment',
    'economic', 'trade', 'corporate', 'sustainability', 'venture'
]

# Technical/STEM keywords
TECH_KEYWORDS = [
    'computer science', 'software engineering', 'data science', 'machine learning',
    'artificial intelligence', 'cybersecurity', 'robotics', 'embedded', 'electrical',
    'mechanical', 'civil engineering', 'chemical engineering', 'physics', 'mathematics',
    'biology', 'bioinformatics', 'medicine', 'health', 'clinical', 'pharmacy',
    'chemistry', 'materials', 'aerospace', 'automotive', 'energy engineering',
    'geoscience', 'ecology', 'zoology', 'botany',
    'linguistics', 'literature', 'history', 'philosophy', 'sociology', 'anthropology',
    'psychology', 'neuroscience', 'cognitive', 'education', 'teaching', 'pedagogy',
    'law', 'legal', 'theology', 'religious', 'arts', 'music',
    'architecture', 'urban planning', 'geography', 'archaeology',
    'informatics', 'hci', 'human computer', 'interaction design',
    'game', 'media informatics', 'network', 'cloud computing', 'distributed systems',
    'algorithm', 'computational', 'quantum', 'statistics', 'econometrics',
    'cs', 'ai', 'ml', 'dl', 'nlp', 'cv', 'iot', 'sql', 'nosql',
    'web', 'mobile', 'app', 'system', 'computing', 'programming', 'coding',
    'automation', 'control', 'signal processing', 'image processing', 'vision',
    'autonomous', 'smart', 'intelligent system', 'knowledge', 'semantic',
    'graph', 'database', 'information system', 'telecommunication', '5g',
    'blockchain', 'crypto', 'virtual', 'augmented', 'xr', 'vr', 'ar',
    'design', 'geoinformatics', 'speech', 'language'
]


def classify_program(program_name, program_url=''):
    """
    Classify a program as 'business' or 'technical'.
    Returns 'business' or 'technical'.
    """
    name_lower = program_name.lower()
    url_lower = program_url.lower() if program_url else ''
    combined = name_lower + ' ' + url_lower

    # Score for each category
    business_score = 0
    tech_score = 0

    # Check for business keywords
    for keyword in BUSINESS_KEYWORDS:
        if keyword in combined:
            business_score += 1

    # Check for technical keywords
    for keyword in TECH_KEYWORDS:
        if keyword in combined:
            tech_score += 1

    # Decision logic
    if tech_score > business_score:
        return 'technical'
    elif business_score > tech_score:
        return 'business'
    elif business_score > 0:
        return 'business'  # Tie-breaker: if any business keywords, call it business
    else:
        return 'technical'  # Default to technical


def filter_discovery_files():
    """Filter discovery files into business and technical."""
    print("=" * 60)
    print("FILTERING DISCOVERY FILES")
    print("=" * 60)

    total_programs = 0
    business_count = 0
    technical_count = 0

    for filename in os.listdir(DISCOVERY_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(DISCOVERY_DIR, filename)
        with open(filepath, 'r') as f:
            programs = json.load(f)

        business_progs = []
        technical_progs = []

        for prog in programs:
            total_programs += 1
            prog_name = prog.get('program_name', '')
            prog_url = prog.get('url', '')

            classification = classify_program(prog_name, prog_url)
            if classification == 'business':
                business_progs.append(prog)
                business_count += 1
            else:
                technical_progs.append(prog)
                technical_count += 1

        # Save business programs
        if business_progs:
            with open(os.path.join(DISCOVERY_BUSINESS_DIR, filename), 'w') as f:
                json.dump(business_progs, f, indent=2)

        # Save technical programs
        if technical_progs:
            with open(os.path.join(DISCOVERY_TECH_DIR, filename), 'w') as f:
                json.dump(technical_progs, f, indent=2)

        print(f"{filename}: {len(business_progs)} business, {len(technical_progs)} technical")

    print(f"\nTotal: {business_count} business, {technical_count} technical, {total_programs} overall")
    return business_count, technical_count, total_programs


def filter_extraction_files():
    """Filter extraction files into business and technical."""
    print("\n" + "=" * 60)
    print("FILTERING EXTRACTION FILES")
    print("=" * 60)

    business_files = 0
    technical_files = 0

    for filename in os.listdir(EXTRACTION_DIR):
        if not filename.endswith('.json'):
            continue

        if '-' not in filename:
            continue

        base = filename[:-5]
        parts = base.split('-', 1)
        if len(parts) != 2:
            continue

        uni_name, prog_name = parts
        prog_name_display = prog_name.replace('-', ' ')

        classification = classify_program(prog_name_display, '')

        src = os.path.join(EXTRACTION_DIR, filename)
        if classification == 'business':
            dst = os.path.join(EXTRACTION_BUSINESS_DIR, filename)
            shutil.copy(src, dst)
            business_files += 1
        else:
            dst = os.path.join(EXTRACTION_TECH_DIR, filename)
            shutil.copy(src, dst)
            technical_files += 1

    print(f"Business: {business_files} files")
    print(f"Technical: {technical_files} files")
    return business_files, technical_files


def main():
    # Clear and recreate output directories
    for d in [DISCOVERY_BUSINESS_DIR, DISCOVERY_TECH_DIR, EXTRACTION_BUSINESS_DIR, EXTRACTION_TECH_DIR]:
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # Filter files
    disc_business, disc_tech, disc_total = filter_discovery_files()
    extr_business, extr_tech = filter_extraction_files()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nDiscovery: {disc_business} business + {disc_tech} technical = {disc_total} total")
    print(f"Extraction: {extr_business} business + {extr_tech} technical = {extr_business + extr_tech} total")
    print(f"\nBusiness folders: {DISCOVERY_BUSINESS_DIR}/, {EXTRACTION_BUSINESS_DIR}/")
    print(f"Technical folders: {DISCOVERY_TECH_DIR}/, {EXTRACTION_TECH_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
