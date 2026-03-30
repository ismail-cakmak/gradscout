#!/usr/bin/env python3
"""Emit the next extraction batch directly from pipeline state and discovery files."""

import argparse
import json
import os
import re
import unicodedata

from sync_pipeline_state import find_discovery_file


DISCOVERY_DIR = ".state/discovery"
STATE_FILE = ".state/pipeline-state.md"
CONTEXT_FILE = "master-context.md"
UNIVERSITY_LINE_RE = re.compile(r"- \[(.)\]\[(.)\] (.+?) \((.+)\)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--university")
    return parser.parse_args()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    ascii_text = re.sub(r"-{2,}", "-", ascii_text).strip("-")
    return ascii_text or "item"


def load_schema() -> dict:
    with open(CONTEXT_FILE, "r", encoding="utf-8") as handle:
        content = handle.read()

    match = re.search(r"## Extraction Schema\s+```json\s*(\{.*?\})\s*```", content, re.DOTALL)
    if not match:
        raise RuntimeError("Could not find JSON schema in master-context.md")

    return json.loads(match.group(1))


def load_universities() -> list[dict[str, str]]:
    universities: list[dict[str, str]] = []
    with open(STATE_FILE, "r", encoding="utf-8") as handle:
        for line in handle:
            match = UNIVERSITY_LINE_RE.match(line)
            if not match:
                continue
            universities.append(
                {
                    "discovery_checked": match.group(1),
                    "extraction_checked": match.group(2),
                    "university_name": match.group(3),
                    "country": match.group(4),
                }
            )
    return universities


def select_university(candidates: list[dict[str, str]], requested: str | None) -> dict[str, str] | None:
    if requested:
        requested_slug = slugify(requested)
        for candidate in candidates:
            if slugify(candidate["university_name"]) == requested_slug:
                return candidate
        return None

    for candidate in candidates:
        if candidate["discovery_checked"] == "x" and candidate["extraction_checked"] != "x":
            return candidate
    return None


def build_program_batch(university: dict[str, str], limit: int, schema: dict) -> dict:
    discovery_files = [
        filename.replace(".json", "")
        for filename in os.listdir(DISCOVERY_DIR)
        if filename.endswith(".json")
    ]
    discovery_slug = find_discovery_file(university["university_name"], discovery_files)
    if not discovery_slug:
        raise RuntimeError(f"No discovery file found for {university['university_name']}")

    discovery_path = os.path.join(DISCOVERY_DIR, f"{discovery_slug}.json")
    with open(discovery_path, "r", encoding="utf-8") as handle:
        programs = json.load(handle)

    pending_programs = [program for program in programs if program.get("status") == "pending"]
    university_slug = slugify(discovery_slug)

    selected_programs = []
    for program in pending_programs[:limit]:
        program_slug = slugify(program.get("program_name", "program"))
        selected_programs.append(
            {
                "program_name": program.get("program_name"),
                "url": program.get("url"),
                "session_name": f"prog-{university_slug}-{program_slug}"[:96],
                "output_file": f".state/extraction/{university_slug}-{program_slug}.json",
            }
        )

    return {
        "done": False,
        "university_name": university["university_name"],
        "country": university["country"],
        "discovery_file": discovery_path,
        "schema": schema,
        "programs": selected_programs,
        "remaining_pending_for_university": max(0, len(pending_programs) - len(selected_programs)),
    }


def main() -> None:
    args = parse_args()
    schema = load_schema()
    universities = load_universities()
    target = select_university(universities, args.university)

    if not target:
        print(json.dumps({"done": True, "programs": []}, indent=2, ensure_ascii=False))
        return

    batch = build_program_batch(target, args.limit, schema)
    print(json.dumps(batch, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
