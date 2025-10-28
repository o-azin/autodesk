# Revit 1M+ Asset Generator

Generate 1M+ realistic Revit assets across 50 tenants with properties matching the Autodesk AEC workload distribution.

## Overview

This generator creates production-scale synthetic Revit data:
- **1,198,800 assets** across 50 tenants
- **3,596,400 relationships** (3:1 asset-to-relationship ratio)
- **50 tenant databases** with realistic distribution:
  - 35 small tenants (17K assets each)
  - 12 medium tenants (~27.6K assets each)
  - 2 large tenants (~130K assets each)
  - 1 enterprise tenant (15.9K assets)
- **Realistic property distribution** matching tenant_0001 data:
  - P50: 287 properties per asset
  - P75: 592 properties per asset
  - P95: 997 properties per asset
  - P99: 4,491 properties per asset
- **8 asset types** matching Autodesk Revit categories
- **Bitemporal schema** (validFrom, validTo, transactionTime)
- **Revit metadata** (elementId, categoryId, phases)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd revit-10k-generator

# No external dependencies required (uses only Python stdlib)
```

### Generate Data

```bash
# Generate all 50 tenants with 1M+ assets
python3 generate_revit_1m_assets.py
```

### Output

The script generates 50 tenant directories in `output/`:

```
output/
├── tenant_0001/
│   ├── assets.json          # 17,000 assets
│   └── relationships.json   # 51,000 relationships
├── tenant_0002/
│   ├── assets.json
│   └── relationships.json
...
└── tenant_0050/
    ├── assets.json          # 15,900 assets
    └── relationships.json   # 47,700 relationships
```

**Total Output:**
- Assets: 1,198,800 (~100 GB raw JSON)
- Relationships: 3,596,400 (~15 GB raw JSON)
- Compressed: ~50 GB (gzip)

## Data Schema

### Asset Document

```json
{
  "assetId": "tenant_revit_10k-asset-000001",
  "revisionId": "tenant_revit_10k-asset-000001-rev-1",
  "validFrom": "2025-10-28T10:00:00.000000",
  "validTo": null,
  "transactionTime": "2025-10-28T10:00:00.000000",
  "tenantId": "tenant_revit_10k",
  "spaceId": "space-level-1",
  "shardKey": "tenant_revit_10k:space-level-1",
  "type": "autodesk.revit:wall-2.0.0",
  "components": {
    "insertions": {
      "metadata": {
        "typeId": "autodesk.revit:element-metadata-1.0.0",
        "staticChildren": {
          "elementId": {"typeId": "String", "value": "1"},
          "categoryId": {"typeId": "String", "value": "OST_Walls"},
          "phaseCreated": {"typeId": "String", "value": "Existing"},
          "phaseDemo": {"typeId": "String", "value": "Phase 1"}
        }
      },
      "geometry": {
        "typeId": "autodesk.geometry:bounds-1.0.0",
        "staticChildren": {
          "minPoint": {"typeId": "Point3d", "value": [10.5, 20.3, 0]},
          "maxPoint": {"typeId": "Point3d", "value": [150.2, 200.5, 12.5]}
        }
      },
      "properties": {
        "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
        "staticChildren": {
          "properties": {
            "typeId": "map<autodesk.parameter:parameter-2.0.0>",
            "insertions": {
              "height": {
                "typeId": "autodesk.revit.parameter:height-1.0.0",
                "staticChildren": {
                  "value": {"typeId": "Float64", "value": 12.5},
                  "unit": {"typeId": "String", "value": "ft"}
                }
              },
              "mark": {
                "typeId": "autodesk.revit.parameter:mark-1.0.0",
                "staticChildren": {
                  "value": {"typeId": "String", "value": "M-1234"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Relationship Document

```json
{
  "relationshipId": "tenant_revit_10k-asset-000001-hosted-tenant_revit_10k-asset-000002",
  "fromAssetId": "tenant_revit_10k-asset-000001",
  "toAssetId": "tenant_revit_10k-asset-000002",
  "relationshipType": "hosted",
  "validFrom": "2025-10-28T10:00:00.000000",
  "validTo": null,
  "transactionTime": "2025-10-28T10:00:00.000000",
  "tenantId": "tenant_revit_10k"
}
```

## Asset Types

Distribution matches Autodesk Revit workload:

| Type | Percentage | Revit Category |
|------|-----------|-----------------|
| Wall | 23% | OST_Walls |
| MEP Component | 20% | OST_MechanicalEquipment |
| Furniture | 23% | OST_Furniture |
| Structural | 11.5% | OST_Structural |
| Room | 8.5% | OST_Rooms |
| Window | 6% | OST_Windows |
| Door | 4% | OST_Doors |
| Fixture | 4% | OST_Fixtures |

## Property Types

Realistic Revit parameters:

- **height** - Float64 (5-20 ft)
- **width** - Float64 (2-50 ft)
- **depth** - Float64 (1-30 ft)
- **area** - Float64 (10-5000 sqft)
- **volume** - Float64 (50-10000 cuft)
- **mark** - String (M-100 to M-9999)
- **comments** - String
- **description** - String
- **fireRating** - String (1-4 hr)
- **material** - String (Concrete, Steel, Wood, Glass, Brick)

## Relationship Types

- `hosted` - Asset hosted in another asset
- `roomBounding` - Asset bounds a room
- `serves` - Asset serves another asset
- `connects` - Asset connects to another
- `contains` - Asset contains another
- `supports` - Asset supports another

## Property Distribution

The generator uses realistic property distribution based on actual Revit data:

```
P50 (50%):   114-287 properties
P75 (75%):   287-592 properties
P95 (95%):   592-997 properties
P99 (99%):   997-4491 properties
```

This matches the distribution from tenant_0001 with 17,000 assets.

## Performance

- **Generation time**: ~2-3 minutes
- **Output size**: ~1.5 GB (uncompressed JSON)
- **Compressed size**: ~900 MB (gzip)

## Usage with MongoDB

### Import to MongoDB Atlas

```bash
# Using mongoimport
mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection assets \
  --file output/assets.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500

mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection relationships \
  --file output/relationships.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500
```

### Create Indexes

```javascript
// Assets collection
db.assets.createIndex({ assetId: 1, validTo: 1 });
db.assets.createIndex({ spaceId: 1, validTo: 1 });
db.assets.createIndex({ type: 1, validTo: 1 });
db.assets.createIndex({ assetId: 1, spaceId: 1, validTo: 1 });

// Relationships collection
db.relationships.createIndex({ fromAssetId: 1, validTo: 1 });
db.relationships.createIndex({ toAssetId: 1, validTo: 1 });
db.relationships.createIndex({ relationshipType: 1, validTo: 1 });
```

## Customization

Edit `generate_revit_10k_assets.py` to customize:

- **Asset count**: Change `range(1, 10001)` to desired count
- **Relationship ratio**: Change `range(30000)` to desired count
- **Property distribution**: Modify `get_property_count()` function
- **Asset types**: Add/remove from `ASSET_TYPES` dictionary
- **Parameters**: Add/remove from `REVIT_PARAMETERS` list
- **Spaces**: Modify `SPACES` list

## Requirements

- Python 3.7+
- No external dependencies (uses only Python stdlib)

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.

## Related

- [Autodesk AEC Workload](https://www.autodesk.com/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [Revit API Documentation](https://www.autodesk.com/developer/revit)

