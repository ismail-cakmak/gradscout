#!/usr/bin/env python3
"""Sync discovery program statuses from extraction files, then refresh pipeline state."""

import json
import os
import re

from sync_pipeline_state import main as sync_pipeline_state_main


DISCOVERY_DIR = ".state/discovery"
EXTRACTION_DIR = ".state/extraction"


def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.lower().strip()
    if url.endswith("/"):
        url = url[:-1]
    return url.replace("https://", "").replace("http://", "").replace("www.", "")


def normalize_program_name(name: str) -> str:
    name = (name or "").lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^\w\s-]", "", name)
    return name


def load_extraction_index() -> tuple[set[str], set[str]]:
    extracted_urls: set[str] = set()
    extracted_names: set[str] = set()

    if not os.path.exists(EXTRACTION_DIR):
        return extracted_urls, extracted_names

    for filename in os.listdir(EXTRACTION_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(EXTRACTION_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            print(f"Error reading extraction file {filename}: {exc}")
            continue

        if isinstance(data, dict):
            url = normalize_url(data.get("program_url", ""))
            name = normalize_program_name(data.get("program_name", ""))
            if url:
                extracted_urls.add(url)
            if name:
                extracted_names.add(name)

    return extracted_urls, extracted_names


def sync_discovery_file(filepath: str, extracted_urls: set[str], extracted_names: set[str]) -> tuple[int, int, int]:
    with open(filepath, "r", encoding="utf-8") as handle:
        programs = json.load(handle)

    done_count = 0
    pending_count = 0
    failed_count = 0
    modified = False

    for program in programs:
        url = normalize_url(program.get("url", ""))
        name = normalize_program_name(program.get("program_name", ""))
        matched = (url and url in extracted_urls) or (name and name in extracted_names)

        current_status = program.get("status", "pending")
        if matched:
            new_status = "done"
        elif current_status == "failed":
            new_status = "failed"
        else:
            new_status = "pending"

        if current_status != new_status:
            program["status"] = new_status
            modified = True

        if new_status == "done":
            done_count += 1
        elif new_status == "failed":
            failed_count += 1
        else:
            pending_count += 1

    if modified:
        with open(filepath, "w", encoding="utf-8") as handle:
            json.dump(programs, handle, indent=2, ensure_ascii=False)

    return done_count, pending_count, failed_count


def main() -> None:
    extracted_urls, extracted_names = load_extraction_index()
    print(
        f"Loaded {len(extracted_urls)} unique extracted URLs and "
        f"{len(extracted_names)} unique extracted names."
    )

    total_done = 0
    total_pending = 0
    total_failed = 0

    for filename in sorted(os.listdir(DISCOVERY_DIR)):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(DISCOVERY_DIR, filename)
        try:
            done_count, pending_count, failed_count = sync_discovery_file(
                filepath, extracted_urls, extracted_names
            )
        except Exception as exc:
            print(f"Error processing {filename}: {exc}")
            continue

        total_done += done_count
        total_pending += pending_count
        total_failed += failed_count

        total_known = done_count + pending_count + failed_count
        if total_known:
            print(
                f"{filename}: {done_count} done, "
                f"{pending_count} pending, {failed_count} failed"
            )

    print(
        f"\nTotal programs: {total_done + total_pending + total_failed}, "
        f"Done: {total_done}, Pending: {total_pending}, Failed: {total_failed}"
    )

    sync_pipeline_state_main()


if __name__ == "__main__":
    main()
