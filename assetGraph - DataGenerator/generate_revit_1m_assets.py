#!/usr/bin/env python3
"""
Generate 1M+ realistic Revit assets across 50 tenants.

This script creates:
- 1,198,800 assets across 50 tenants (matching production distribution)
- 3,596,400 relationships (3:1 ratio)
- Property distribution: P50: 287, P75: 592, P95: 997, P99: 4491
- 8 asset types matching Autodesk Revit categories
- Realistic Revit metadata (elementId, categoryId, phases)

Tenant Distribution:
- Small (35 tenants): 17,000 assets each
- Medium (12 tenants): ~27,600 assets each
- Large (2 tenants): ~130,200 assets each
- Enterprise (1 tenant): 15,900 assets

Output:
- output/tenant_0001/assets.json + relationships.json
- output/tenant_0002/assets.json + relationships.json
- ... (50 tenant directories)

Usage:
    python3 generate_revit_1m_assets.py
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Asset type distribution (matching Revit workload)
ASSET_TYPES = [
    {'type': 'wall', 'typeId': 'autodesk.revit:wall-2.0.0', 'category': 'Walls', 'weight': 0.23},
    {'type': 'mep', 'typeId': 'autodesk.revit:mep-component-2.0.0', 'category': 'MEP', 'weight': 0.20},
    {'type': 'furniture', 'typeId': 'autodesk.revit:furniture-2.0.0', 'category': 'Furniture', 'weight': 0.23},
    {'type': 'structural', 'typeId': 'autodesk.revit:structural-2.0.0', 'category': 'Structural', 'weight': 0.115},
    {'type': 'room', 'typeId': 'autodesk.revit:room-2.0.0', 'category': 'Rooms', 'weight': 0.085},
    {'type': 'window', 'typeId': 'autodesk.revit:window-2.0.0', 'category': 'Windows', 'weight': 0.06},
    {'type': 'door', 'typeId': 'autodesk.revit:door-2.0.0', 'category': 'Doors', 'weight': 0.04},
    {'type': 'fixture', 'typeId': 'autodesk.revit:fixture-2.0.0', 'category': 'Fixtures', 'weight': 0.04},
]

RELATIONSHIP_TYPES = ['hosted', 'roomBounding', 'serves', 'connects', 'contains', 'supports']
SPACES = [f'space-level-{i}' for i in range(1, 6)]
PHASES = ['Existing', 'Phase 1', 'Phase 2', 'Phase 3']

def get_property_count() -> int:
    """Generate property count based on realistic distribution from tenant_0001."""
    rand = random.random()
    if rand < 0.50:
        return random.randint(114, 287)
    elif rand < 0.75:
        return random.randint(287, 592)
    elif rand < 0.95:
        return random.randint(592, 997)
    else:
        return random.randint(997, 4491)

def generate_properties(count: int) -> Dict[str, Any]:
    """Generate realistic Revit properties."""
    properties = {}
    property_types = [
        ('area', 'Float64', lambda: round(random.uniform(50, 500), 2)),
        ('volume', 'Float64', lambda: round(random.uniform(100, 1000), 2)),
        ('length', 'Float64', lambda: round(random.uniform(5, 50), 2)),
        ('width', 'Float64', lambda: round(random.uniform(0.5, 2), 2)),
        ('height', 'Float64', lambda: round(random.uniform(8, 14), 2)),
        ('cost', 'Float64', lambda: round(random.uniform(100, 10000), 2)),
        ('mark', 'String', lambda: f"M-{random.randint(1, 999)}"),
        ('comments', 'String', lambda: random.choice(['Approved', 'Pending', 'Review'])),
    ]
    
    for i in range(count):
        prop_name, value_type, value_gen = random.choice(property_types)
        prop_key = f"{prop_name}_{i}" if i > 0 else prop_name
        properties[prop_key] = {
            'typeId': f'autodesk.revit.parameter:{prop_name}-1.0.0',
            'staticChildren': {
                'value': {'typeId': value_type, 'value': value_gen()}
            }
        }
    
    return properties

def generate_asset(tenant_id: str, asset_num: int, space_id: str, asset_type: Dict) -> Dict[str, Any]:
    """Generate a single realistic Revit asset."""
    asset_id = f"{tenant_id}-asset-{asset_num:06d}"
    revision_id = f"{asset_id}-rev-1"
    now = datetime.utcnow().isoformat() + "Z"
    
    prop_count = get_property_count()
    properties = generate_properties(prop_count)
    
    return {
        'assetId': asset_id,
        'revisionId': revision_id,
        'validFrom': now,
        'validTo': None,
        'transactionTime': now,
        'tenantId': tenant_id,
        'spaceId': space_id,
        'shardKey': f"{tenant_id}:{space_id}",
        'type': asset_type['typeId'],
        'components': {
            'insertions': {
                'metadata': {
                    'typeId': 'autodesk.revit:element-metadata-1.0.0',
                    'staticChildren': {
                        'elementId': {'typeId': 'String', 'value': str(asset_num)},
                        'categoryId': {'typeId': 'String', 'value': f"OST_{asset_type['category']}"},
                        'phaseCreated': {'typeId': 'String', 'value': random.choice(PHASES)},
                        'phaseDemo': {'typeId': 'String', 'value': random.choice(PHASES)}
                    }
                },
                'geometry': {
                    'typeId': 'autodesk.geometry:bounds-1.0.0',
                    'staticChildren': {
                        'minPoint': {'typeId': 'Point3d', 'value': [
                            round(random.uniform(0, 100), 2),
                            round(random.uniform(0, 100), 2),
                            0
                        ]},
                        'maxPoint': {'typeId': 'Point3d', 'value': [
                            round(random.uniform(100, 200), 2),
                            round(random.uniform(100, 200), 2),
                            round(random.uniform(8, 14), 2)
                        ]}
                    }
                },
                'properties': {
                    'typeId': 'autodesk.aec:component.propertyGroup-1.1.0',
                    'staticChildren': {
                        'properties': {
                            'typeId': 'map<autodesk.parameter:parameter-2.0.0>',
                            'insertions': properties
                        }
                    }
                }
            }
        }
    }

def generate_relationship(tenant_id: str, rel_num: int, source_asset_id: str, target_asset_id: str) -> Dict[str, Any]:
    """Generate a single relationship."""
    rel_id = f"{tenant_id}-rel-{rel_num:06d}"
    now = datetime.utcnow().isoformat() + "Z"
    
    return {
        'relationshipId': rel_id,
        'tenantId': tenant_id,
        'fromAssetId': source_asset_id,
        'toAssetId': target_asset_id,
        'relationshipType': random.choice(RELATIONSHIP_TYPES),
        'validFrom': now,
        'validTo': None,
        'transactionTime': now
    }

def generate_tenant_manifest() -> List[Dict[str, Any]]:
    """Generate tenant manifest matching production distribution."""
    tenants = []
    
    # Small tenants (35): 17,000 assets each
    for i in range(35):
        tenants.append({
            'tenant_id': f'tenant_{i+1:04d}',
            'asset_count': 17_000,
            'relationship_count': 51_000,
            'category': 'small'
        })
    
    # Medium tenants (12): ~27,600 assets each
    for i in range(12):
        tenants.append({
            'tenant_id': f'tenant_{35+i+1:04d}',
            'asset_count': 27_616,
            'relationship_count': 82_848,
            'category': 'medium'
        })
    
    # Large tenants (2): ~130,200 assets each
    for i in range(2):
        tenants.append({
            'tenant_id': f'tenant_{47+i+1:04d}',
            'asset_count': 130_200,
            'relationship_count': 390_600,
            'category': 'large'
        })
    
    # Enterprise tenant (1): 15,900 assets
    tenants.append({
        'tenant_id': 'tenant_0050',
        'asset_count': 15_900,
        'relationship_count': 47_700,
        'category': 'enterprise'
    })
    
    return tenants

def main():
    """Generate 1M+ Revit assets across 50 tenants."""
    print("\n" + "="*80)
    print("REVIT 1M+ ASSET GENERATOR (50 TENANTS)")
    print("="*80)
    
    tenants = generate_tenant_manifest()
    total_assets = sum(t['asset_count'] for t in tenants)
    total_rels = sum(t['relationship_count'] for t in tenants)
    
    print(f"\n📊 Configuration:")
    print(f"  Tenants: {len(tenants)}")
    print(f"  Total Assets: {total_assets:,}")
    print(f"  Total Relationships: {total_rels:,}")
    print(f"  Output: output/tenant_*/")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    start_time = datetime.now()
    total_assets_generated = 0
    total_rels_generated = 0
    
    for tenant_idx, tenant in enumerate(tenants, 1):
        tenant_id = tenant['tenant_id']
        num_assets = tenant['asset_count']
        num_rels = tenant['relationship_count']
        
        print(f"\n[{tenant_idx:2d}/{len(tenants)}] {tenant_id} ({tenant['category']:10s}): {num_assets:,} assets, {num_rels:,} rels")
        
        tenant_dir = output_dir / tenant_id
        tenant_dir.mkdir(exist_ok=True)
        
        # Generate assets
        assets = []
        for i in range(num_assets):
            asset_type = random.choices(ASSET_TYPES, weights=[t['weight'] for t in ASSET_TYPES])[0]
            space_id = random.choice(SPACES)
            asset = generate_asset(tenant_id, i + 1, space_id, asset_type)
            assets.append(asset)
            
            if (i + 1) % 10000 == 0:
                print(f"  ✓ {i + 1:,}/{num_assets:,} assets")
        
        assets_file = tenant_dir / "assets.json"
        with open(assets_file, 'w') as f:
            json.dump(assets, f)
        
        assets_size_mb = assets_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ Saved {len(assets):,} assets ({assets_size_mb:.1f} MB)")
        
        # Generate relationships
        relationships = []
        for i in range(num_rels):
            source_idx = random.randint(0, num_assets - 1)
            target_idx = random.randint(0, num_assets - 1)
            source_asset_id = f"{tenant_id}-asset-{source_idx + 1:06d}"
            target_asset_id = f"{tenant_id}-asset-{target_idx + 1:06d}"
            relationship = generate_relationship(tenant_id, i + 1, source_asset_id, target_asset_id)
            relationships.append(relationship)
            
            if (i + 1) % 20000 == 0:
                print(f"  ✓ {i + 1:,}/{num_rels:,} relationships")
        
        rels_file = tenant_dir / "relationships.json"
        with open(rels_file, 'w') as f:
            json.dump(relationships, f)
        
        rels_size_mb = rels_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ Saved {len(relationships):,} relationships ({rels_size_mb:.1f} MB)")
        
        total_assets_generated += len(assets)
        total_rels_generated += len(relationships)
    
    total_time = (datetime.now() - start_time).total_seconds()
    
    print(f"\n" + "="*80)
    print(f"✅ GENERATION COMPLETE")
    print(f"="*80)
    print(f"  Tenants: {len(tenants)}")
    print(f"  Total Assets: {total_assets_generated:,}")
    print(f"  Total Relationships: {total_rels_generated:,}")
    print(f"  Time: {total_time/60:.1f} minutes")
    print(f"  Rate: {(total_assets_generated + total_rels_generated)/total_time:.0f} docs/sec")
    print(f"\n📁 Output: {output_dir}/")
    print(f"="*80 + "\n")

if __name__ == '__main__':
    main()

