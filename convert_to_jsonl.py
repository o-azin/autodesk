#!/usr/bin/env python3
"""
Convert JSON array files to JSONL format for mongoimport.

MongoDB's mongoimport has issues with --jsonArray when using compound _id fields.
This script converts the JSON array files to JSONL (one JSON object per line).
"""

import json
import sys
from pathlib import Path


def convert_to_jsonl(input_file: str, output_file: str):
    """Convert JSON array file to JSONL format."""
    print(f"Converting {input_file} to {output_file}...")
    
    # Read JSON array
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"Error: {input_file} is not a JSON array")
        return False
    
    # Write as JSONL (one JSON object per line)
    with open(output_file, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✓ Converted {len(data)} documents")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_to_jsonl.py <directory>")
        print("Example: python3 convert_to_jsonl.py test_import")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    
    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)
    
    print(f"Converting files in {input_dir} to JSONL format...")
    print("=" * 60)
    
    # Convert assets.json
    assets_json = input_dir / "assets.json"
    assets_jsonl = input_dir / "assets.jsonl"
    if assets_json.exists():
        convert_to_jsonl(assets_json, assets_jsonl)
    else:
        print(f"Warning: {assets_json} not found")
    
    # Convert relationships.json
    relationships_json = input_dir / "relationships.json"
    relationships_jsonl = input_dir / "relationships.jsonl"
    if relationships_json.exists():
        convert_to_jsonl(relationships_json, relationships_jsonl)
    else:
        print(f"Warning: {relationships_json} not found")
    
    print("=" * 60)
    print("✓ Conversion complete!")
    print()
    print("Import to MongoDB:")
    print(f"  cd {input_dir}")
    print(f"  mongoimport --db=<db_name> --collection=models --file=model.json")
    print(f"  mongoimport --db=<db_name> --collection=assets --file=assets.jsonl")
    print(f"  mongoimport --db=<db_name> --collection=relationships --file=relationships.jsonl")


if __name__ == "__main__":
    main()

