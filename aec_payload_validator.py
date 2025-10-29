#!/usr/bin/env python3
"""
Validation script to compare generated payload with sample structure.
"""

import json
import sys


def validate_payload(file_path):
    """Validate the structure of a generated payload."""
    print(f"Validating {file_path}...")
    print("=" * 60)
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return False
    
    # Check top-level structure
    required_keys = ['batchId', 'description', 'modelStatistics', 'entityDistribution', 
                     'commands', 'relationships', 'batchProcessingInfo']
    
    print("\n1. Checking top-level structure...")
    for key in required_keys:
        if key in data:
            print(f"  ✓ {key}")
        else:
            print(f"  ❌ Missing: {key}")
            return False
    
    # Check model statistics
    print("\n2. Checking model statistics...")
    stats = data['modelStatistics']
    print(f"  Total Entities: {stats.get('totalEntities', 'N/A')}")
    print(f"  Model Size: {stats.get('modelSize', 'N/A')}")
    print(f"  Average Asset Size: {stats.get('averageAssetSize', 'N/A')}")
    print(f"  Batch Count: {stats.get('batchCount', 'N/A')}")
    
    # Check entity distribution
    print("\n3. Checking entity distribution...")
    dist = data['entityDistribution']
    total_from_dist = sum(dist.values())
    print(f"  Total from distribution: {total_from_dist}")
    for entity_type, count in dist.items():
        print(f"    {entity_type}: {count}")
    
    # Check commands structure
    print("\n4. Checking commands structure...")
    if not data['commands']:
        print("  ❌ No commands found")
        return False
    
    command = data['commands'][0]
    print(f"  Command Type: {command.get('commandType', 'N/A')}")
    print(f"  Assets Count: {len(command.get('assets', []))}")
    
    # Validate first asset structure
    if command.get('assets'):
        asset = command['assets'][0]
        print(f"\n5. Validating first asset structure...")
        print(f"  ID: {asset.get('id', 'N/A')}")
        print(f"  Type: {asset.get('type', 'N/A')}")
        
        required_asset_keys = ['id', 'type', 'space', 'attributes', 'components']
        for key in required_asset_keys:
            if key in asset:
                print(f"  ✓ {key}")
            else:
                print(f"  ❌ Missing: {key}")
        
        # Check components structure
        if 'components' in asset and 'insertions' in asset['components']:
            insertions = asset['components']['insertions']
            print(f"\n  Component insertions:")
            for key in insertions.keys():
                print(f"    ✓ {key}")
    
    # Check relationships
    print(f"\n6. Checking relationships...")
    relationships = data.get('relationships', [])
    print(f"  Total Relationships: {len(relationships)}")
    
    if relationships:
        rel = relationships[0]
        print(f"  First relationship:")
        print(f"    ID: {rel.get('id', 'N/A')}")
        print(f"    Type: {rel.get('type', 'N/A')}")
        print(f"    From: {rel.get('from', {}).get('assetId', 'N/A')}")
        print(f"    To: {rel.get('to', {}).get('assetId', 'N/A')}")
        
        # Count relationship types
        rel_types = {}
        for r in relationships:
            rel_type = r.get('attributes', {}).get('application', {}).get('relationshipType', 'unknown')
            rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
        
        print(f"\n  Relationship type distribution:")
        for rel_type, count in rel_types.items():
            print(f"    {rel_type}: {count}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Validation complete!")
    print(f"  Total Assets: {len(command.get('assets', []))}")
    print(f"  Total Relationships: {len(relationships)}")
    print(f"  File Size: {stats.get('modelSize', 'N/A')}")
    print("=" * 60)
    
    return True


def compare_payloads(file1, file2):
    """Compare two payload files."""
    print(f"\nComparing {file1} and {file2}...")
    print("=" * 60)
    
    try:
        with open(file1, 'r') as f:
            data1 = json.load(f)
        with open(file2, 'r') as f:
            data2 = json.load(f)
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return
    
    # Compare structure
    print("\nStructural Comparison:")
    print(f"  File 1 Assets: {len(data1['commands'][0]['assets'])}")
    print(f"  File 2 Assets: {len(data2['commands'][0]['assets'])}")
    print(f"  File 1 Relationships: {len(data1.get('relationships', []))}")
    print(f"  File 2 Relationships: {len(data2.get('relationships', []))}")
    
    # Compare entity distribution
    print("\nEntity Distribution Comparison:")
    dist1 = data1.get('entityDistribution', {})
    dist2 = data2.get('entityDistribution', {})
    
    all_types = set(list(dist1.keys()) + list(dist2.keys()))
    for entity_type in sorted(all_types):
        count1 = dist1.get(entity_type, 0)
        count2 = dist2.get(entity_type, 0)
        match = "✓" if count1 == count2 else "✗"
        print(f"  {match} {entity_type}: {count1} vs {count2}")
    
    print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate AEC payload files')
    parser.add_argument('file', help='Payload file to validate')
    parser.add_argument('--compare', help='Compare with another payload file')
    
    args = parser.parse_args()
    
    # Validate the file
    if not validate_payload(args.file):
        sys.exit(1)
    
    # Compare if requested
    if args.compare:
        compare_payloads(args.file, args.compare)


if __name__ == '__main__':
    main()

