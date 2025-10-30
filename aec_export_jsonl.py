#!/usr/bin/env python3
"""
AEC JSONL Export Script
Converts individual JSON documents to JSONL format for bulk MongoDB import.

Usage:
    python3 aec_export_jsonl.py --input-dir aec_output --output-dir aec_jsonl
"""

import json
import os
from pathlib import Path
import argparse


def export_to_jsonl(input_dir: str, output_dir: str = None):
    """
    Export individual JSON documents to JSONL files.
    
    Args:
        input_dir: Directory containing model.json, assets/, and relationships/
        output_dir: Output directory for JSONL files (default: input_dir)
    """
    print("=" * 60)
    print("AEC JSONL Export")
    print("=" * 60)
    
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Verify directory structure
    if not input_path.exists():
        print(f"❌ Error: Directory not found: {input_dir}")
        return False
    
    model_file = input_path / "model.json"
    assets_dir = input_path / "assets"
    relationships_dir = input_path / "relationships"
    
    if not model_file.exists():
        print(f"❌ Error: model.json not found in {input_dir}")
        return False
    
    # Load model document
    print(f"\nLoading model document...")
    with open(model_file, 'r') as f:
        model_doc = json.load(f)
    
    model_id = model_doc['modelId']
    print(f"  Model ID: {model_id}")
    
    # Export model to JSONL
    models_jsonl = output_path / "models.jsonl"
    print(f"\nExporting model to {models_jsonl}...")
    with open(models_jsonl, 'w') as f:
        f.write(json.dumps(model_doc) + '\n')
    print(f"✓ Model exported (1 document)")
    
    # Export assets to JSONL
    if assets_dir.exists():
        assets_jsonl = output_path / "assets.jsonl"
        print(f"\nExporting assets to {assets_jsonl}...")
        
        asset_files = list(assets_dir.glob("*.json"))
        print(f"  Found {len(asset_files)} asset files")
        
        assets_exported = 0
        with open(assets_jsonl, 'w') as f:
            for asset_file in asset_files:
                with open(asset_file, 'r') as af:
                    asset_doc = json.load(af)
                    f.write(json.dumps(asset_doc) + '\n')
                    assets_exported += 1
                
                if assets_exported % 1000 == 0:
                    print(f"  Exported {assets_exported}/{len(asset_files)} assets...")
        
        print(f"✓ Assets exported ({assets_exported} documents)")
    
    # Export relationships to JSONL
    if relationships_dir.exists():
        relationships_jsonl = output_path / "relationships.jsonl"
        print(f"\nExporting relationships to {relationships_jsonl}...")
        
        rel_files = list(relationships_dir.glob("*.json"))
        print(f"  Found {len(rel_files)} relationship files")
        
        relationships_exported = 0
        with open(relationships_jsonl, 'w') as f:
            for rel_file in rel_files:
                with open(rel_file, 'r') as rf:
                    rel_doc = json.load(rf)
                    f.write(json.dumps(rel_doc) + '\n')
                    relationships_exported += 1
                
                if relationships_exported % 1000 == 0:
                    print(f"  Exported {relationships_exported}/{len(rel_files)} relationships...")
        
        print(f"✓ Relationships exported ({relationships_exported} documents)")
    
    # Create import script
    import_script = output_path / "import_to_mongodb.sh"
    print(f"\nCreating MongoDB import script: {import_script}...")
    
    script_content = f"""#!/bin/bash
# MongoDB Import Script
# Generated for model: {model_id}

DB_NAME="${{1:-aec_models}}"
MONGO_URI="${{2:-mongodb://localhost:27017}}"

echo "Importing to database: $DB_NAME"
echo "MongoDB URI: $MONGO_URI"
echo ""

# Import models
echo "Importing models..."
mongoimport --uri="$MONGO_URI" --db="$DB_NAME" --collection=models --file=models.jsonl --mode=upsert --upsertFields=modelId

# Import assets
echo "Importing assets..."
mongoimport --uri="$MONGO_URI" --db="$DB_NAME" --collection=assets --file=assets.jsonl --mode=upsert --upsertFields=modelId,id

# Import relationships
echo "Importing relationships..."
mongoimport --uri="$MONGO_URI" --db="$DB_NAME" --collection=relationships --file=relationships.jsonl --mode=upsert --upsertFields=modelId,id

echo ""
echo "Import complete!"
echo "Database: $DB_NAME"
echo ""
echo "Create indexes with:"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.models.createIndex({{modelId: 1}}, {{unique: true}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.assets.createIndex({{modelId: 1, id: 1}}, {{unique: true}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.assets.createIndex({{modelId: 1}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.assets.createIndex({{type: 1}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.relationships.createIndex({{modelId: 1, id: 1}}, {{unique: true}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.relationships.createIndex({{modelId: 1}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.relationships.createIndex({{\\"from.assetId\\": 1}})'"
echo "  mongo $MONGO_URI/$DB_NAME --eval 'db.relationships.createIndex({{\\"to.assetId\\": 1}})'"
"""
    
    with open(import_script, 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(import_script, 0o755)
    print(f"✓ Import script created")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ JSONL export complete!")
    print(f"  Output directory: {output_path}")
    print(f"  Files created:")
    print(f"    - models.jsonl")
    print(f"    - assets.jsonl")
    print(f"    - relationships.jsonl")
    print(f"    - import_to_mongodb.sh")
    print("\n  To import to MongoDB:")
    print(f"    cd {output_path}")
    print(f"    ./import_to_mongodb.sh [db_name] [mongo_uri]")
    print("=" * 60)
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export AEC documents to JSONL format',
        epilog='Example: python3 aec_export_jsonl.py --input-dir aec_output'
    )
    parser.add_argument('--input-dir', type=str, required=True,
                       help='Input directory containing model.json, assets/, and relationships/')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory for JSONL files (default: same as input-dir)')
    
    args = parser.parse_args()
    
    success = export_to_jsonl(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )
    
    if not success:
        exit(1)


if __name__ == '__main__':
    main()

