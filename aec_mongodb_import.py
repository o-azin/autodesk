#!/usr/bin/env python3
"""
AEC MongoDB Import Script
Imports individual asset and relationship documents into MongoDB collections.

Usage:
    python3 aec_mongodb_import.py --input-dir aec_output --db-name aec_models
"""

import json
import os
from pathlib import Path
from typing import Dict, List
import argparse


def import_to_mongodb(input_dir: str, db_name: str = "aec_models", 
                      connection_string: str = "mongodb://localhost:27017/"):
    """
    Import AEC documents to MongoDB.
    
    Args:
        input_dir: Directory containing model.json, assets/, and relationships/
        db_name: MongoDB database name
        connection_string: MongoDB connection string
    """
    try:
        from pymongo import MongoClient
        from pymongo.errors import BulkWriteError
    except ImportError:
        print("❌ Error: pymongo not installed")
        print("Install with: pip install pymongo")
        return False
    
    print("=" * 60)
    print("AEC MongoDB Import")
    print("=" * 60)
    
    input_path = Path(input_dir)
    
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
    
    if not assets_dir.exists():
        print(f"❌ Error: assets/ directory not found in {input_dir}")
        return False
    
    if not relationships_dir.exists():
        print(f"❌ Error: relationships/ directory not found in {input_dir}")
        return False
    
    # Connect to MongoDB
    print(f"\nConnecting to MongoDB: {connection_string}")
    try:
        client = MongoClient(connection_string)
        db = client[db_name]
        print(f"✓ Connected to database: {db_name}")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False
    
    # Load model document
    print(f"\nLoading model document...")
    with open(model_file, 'r') as f:
        model_doc = json.load(f)
    
    model_id = model_doc['modelId']
    print(f"  Model ID: {model_id}")
    print(f"  Total Assets: {model_doc['generationInfo']['totalAssets']}")
    print(f"  Total Relationships: {model_doc['generationInfo']['totalRelationships']}")
    
    # Import model document
    models_collection = db['models']
    print(f"\nImporting model document to 'models' collection...")
    models_collection.replace_one(
        {'modelId': model_id},
        model_doc,
        upsert=True
    )
    print(f"✓ Model document imported")
    
    # Import assets
    assets_collection = db['assets']
    print(f"\nImporting assets from {assets_dir}...")
    
    asset_files = list(assets_dir.glob("*.json"))
    print(f"  Found {len(asset_files)} asset files")
    
    batch_size = 1000
    assets_imported = 0
    
    for i in range(0, len(asset_files), batch_size):
        batch_files = asset_files[i:i + batch_size]
        batch_docs = []
        
        for asset_file in batch_files:
            with open(asset_file, 'r') as f:
                asset_doc = json.load(f)
                batch_docs.append(asset_doc)
        
        try:
            if batch_docs:
                # Use replace_one with upsert for each document to avoid duplicates
                for doc in batch_docs:
                    assets_collection.replace_one(
                        {'modelId': doc['modelId'], 'id': doc['id']},
                        doc,
                        upsert=True
                    )
                assets_imported += len(batch_docs)
                print(f"  Imported {assets_imported}/{len(asset_files)} assets...")
        except BulkWriteError as e:
            print(f"  Warning: Some duplicates skipped in batch")
            assets_imported += len(batch_docs)
    
    print(f"✓ Imported {assets_imported} assets to 'assets' collection")
    
    # Import relationships
    relationships_collection = db['relationships']
    print(f"\nImporting relationships from {relationships_dir}...")
    
    rel_files = list(relationships_dir.glob("*.json"))
    print(f"  Found {len(rel_files)} relationship files")
    
    relationships_imported = 0
    
    for i in range(0, len(rel_files), batch_size):
        batch_files = rel_files[i:i + batch_size]
        batch_docs = []
        
        for rel_file in batch_files:
            with open(rel_file, 'r') as f:
                rel_doc = json.load(f)
                batch_docs.append(rel_doc)
        
        try:
            if batch_docs:
                for doc in batch_docs:
                    relationships_collection.replace_one(
                        {'modelId': doc['modelId'], 'id': doc['id']},
                        doc,
                        upsert=True
                    )
                relationships_imported += len(batch_docs)
                print(f"  Imported {relationships_imported}/{len(rel_files)} relationships...")
        except BulkWriteError as e:
            print(f"  Warning: Some duplicates skipped in batch")
            relationships_imported += len(batch_docs)
    
    print(f"✓ Imported {relationships_imported} relationships to 'relationships' collection")
    
    # Create indexes
    print(f"\nCreating indexes...")
    
    # Model indexes
    models_collection.create_index('modelId', unique=True)
    print(f"  ✓ Created index on models.modelId")
    
    # Asset indexes
    assets_collection.create_index([('modelId', 1), ('id', 1)], unique=True)
    assets_collection.create_index('modelId')
    assets_collection.create_index('type')
    print(f"  ✓ Created indexes on assets collection")
    
    # Relationship indexes
    relationships_collection.create_index([('modelId', 1), ('id', 1)], unique=True)
    relationships_collection.create_index('modelId')
    relationships_collection.create_index('from.assetId')
    relationships_collection.create_index('to.assetId')
    relationships_collection.create_index('type')
    print(f"  ✓ Created indexes on relationships collection")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Import complete!")
    print(f"  Database: {db_name}")
    print(f"  Collections:")
    print(f"    - models: {models_collection.count_documents({'modelId': model_id})} document(s)")
    print(f"    - assets: {assets_collection.count_documents({'modelId': model_id})} document(s)")
    print(f"    - relationships: {relationships_collection.count_documents({'modelId': model_id})} document(s)")
    print("=" * 60)
    
    return True


def export_sample_queries(db_name: str = "aec_models"):
    """Generate sample MongoDB queries."""
    
    queries = f"""
# Sample MongoDB Queries for {db_name}

## Get model information
db.models.findOne({{"modelId": "model-20251030-082305"}})

## Count assets by type
db.assets.aggregate([
  {{ $match: {{ modelId: "model-20251030-082305" }} }},
  {{ $group: {{ _id: "$type", count: {{ $sum: 1 }} }} }},
  {{ $sort: {{ count: -1 }} }}
])

## Find all walls
db.assets.find({{
  modelId: "model-20251030-082305",
  type: "autodesk.revit:wall-2.0.0"
}})

## Find all doors in walls (hosted relationships)
db.relationships.find({{
  modelId: "model-20251030-082305",
  type: "autodesk.revit:hosted-1.0.0",
  "attributes.application.relationshipType": "hosted"
}})

## Find all assets in a specific room
db.relationships.aggregate([
  {{ $match: {{ 
    modelId: "model-20251030-082305",
    "to.assetId": {{ $regex: "^room-" }}
  }} }},
  {{ $lookup: {{
    from: "assets",
    localField: "from.assetId",
    foreignField: "id",
    as: "asset"
  }} }},
  {{ $unwind: "$asset" }}
])

## Count relationships by type
db.relationships.aggregate([
  {{ $match: {{ modelId: "model-20251030-082305" }} }},
  {{ $group: {{ 
    _id: "$attributes.application.relationshipType", 
    count: {{ $sum: 1 }} 
  }} }},
  {{ $sort: {{ count: -1 }} }}
])

## Find all assets on a specific level
db.assets.find({{
  modelId: "model-20251030-082305",
  "space.id": "space-building-level-1"
}})
"""
    
    return queries


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Import AEC documents to MongoDB',
        epilog='Example: python3 aec_mongodb_import.py --input-dir aec_output --db-name aec_models'
    )
    parser.add_argument('--input-dir', type=str, required=True,
                       help='Input directory containing model.json, assets/, and relationships/')
    parser.add_argument('--db-name', type=str, default='aec_models',
                       help='MongoDB database name (default: aec_models)')
    parser.add_argument('--connection-string', type=str, default='mongodb://localhost:27017/',
                       help='MongoDB connection string (default: mongodb://localhost:27017/)')
    parser.add_argument('--export-queries', action='store_true',
                       help='Export sample queries to file')
    
    args = parser.parse_args()
    
    # Import to MongoDB
    success = import_to_mongodb(
        input_dir=args.input_dir,
        db_name=args.db_name,
        connection_string=args.connection_string
    )
    
    if not success:
        exit(1)
    
    # Export sample queries if requested
    if args.export_queries:
        queries_file = Path(args.input_dir) / "sample_queries.md"
        with open(queries_file, 'w') as f:
            f.write(export_sample_queries(args.db_name))
        print(f"\n✓ Sample queries exported to: {queries_file}")


if __name__ == '__main__':
    main()

