# Usage Examples

## Basic Generation

### Generate with default settings

```bash
python3 generate_revit_10k_assets.py
```

Output:
```
Generating 10K Revit assets for tenant_revit_10k...
Property distribution: P50: 287, P75: 592, P95: 997, P99: 4491
  Generated 1000 assets...
  Generated 2000 assets...
  ...
  Generated 10000 assets...
✓ Saved 10000 assets to output/assets.json

Generating 30K relationships (3:1 ratio)...
  Generated 10000 relationships...
  Generated 20000 relationships...
  Generated 30000 relationships...
✓ Saved 30000 relationships to output/relationships.json

============================================================
GENERATION COMPLETE
============================================================
Tenant ID: tenant_revit_10k
Assets: 10000
Relationships: 30000
Asset Types: 8
Spaces: 5

Property Distribution:
  Min: 114
  Max: 4491
  Avg: 522
  P50: 287
  P75: 592
  P95: 997
```

### Generate with custom tenant ID

```bash
python3 generate_revit_10k_assets.py tenant_client_acme
```

### Generate with custom output directory

```bash
python3 generate_revit_10k_assets.py tenant_client_acme ./data/acme
```

---

## MongoDB Import

### 1. Create Database and Collections

```bash
# Connect to MongoDB Atlas
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/"

# Create database and collections
use tenant_revit_10k
db.createCollection("assets")
db.createCollection("relationships")
```

### 2. Import Data with mongoimport

```bash
# Import assets
mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection assets \
  --file output/assets.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500 \
  --drop

# Import relationships
mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection relationships \
  --file output/relationships.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500 \
  --drop
```

### 3. Create Indexes

```bash
# Connect to MongoDB
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k"

# Create indexes on assets
db.assets.createIndex({ assetId: 1, validTo: 1 })
db.assets.createIndex({ spaceId: 1, validTo: 1 })
db.assets.createIndex({ type: 1, validTo: 1 })
db.assets.createIndex({ assetId: 1, spaceId: 1, validTo: 1 })
db.assets.createIndex({ tenantId: 1, validTo: 1 })

# Create indexes on relationships
db.relationships.createIndex({ fromAssetId: 1, validTo: 1 })
db.relationships.createIndex({ toAssetId: 1, validTo: 1 })
db.relationships.createIndex({ relationshipType: 1, validTo: 1 })
db.relationships.createIndex({ tenantId: 1, validTo: 1 })
```

### 4. Verify Import

```bash
# Connect to MongoDB
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k"

# Check counts
db.assets.countDocuments()           # Should be 10000
db.relationships.countDocuments()    # Should be 30000

# Check sample asset
db.assets.findOne()

# Check sample relationship
db.relationships.findOne()

# Check asset types distribution
db.assets.aggregate([
  { $group: { _id: "$type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

# Check property distribution
db.assets.aggregate([
  {
    $project: {
      propertyCount: {
        $size: {
          $objectToArray: {
            $getField: {
              field: "insertions",
              input: {
                $getField: {
                  field: "properties",
                  input: {
                    $getField: {
                      field: "staticChildren",
                      input: {
                        $getField: {
                          field: "properties",
                          input: "$components"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  { $group: { _id: null, avg: { $avg: "$propertyCount" }, min: { $min: "$propertyCount" }, max: { $max: "$propertyCount" } } }
])
```

---

## Python Usage

### Import and Use in Python

```python
import json
from pathlib import Path

# Load generated data
with open('output/assets.json', 'r') as f:
    assets = json.load(f)

with open('output/relationships.json', 'r') as f:
    relationships = json.load(f)

# Analyze assets
print(f"Total assets: {len(assets)}")
print(f"Total relationships: {len(relationships)}")

# Get asset types
asset_types = {}
for asset in assets:
    asset_type = asset['type']
    asset_types[asset_type] = asset_types.get(asset_type, 0) + 1

print("\nAsset types distribution:")
for asset_type, count in sorted(asset_types.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(assets)) * 100
    print(f"  {asset_type}: {count} ({percentage:.1f}%)")

# Analyze properties
property_counts = []
for asset in assets:
    try:
        props = asset['components']['insertions']['properties']['staticChildren']['properties']['insertions']
        property_counts.append(len(props))
    except:
        pass

print(f"\nProperty distribution:")
print(f"  Min: {min(property_counts)}")
print(f"  Max: {max(property_counts)}")
print(f"  Avg: {sum(property_counts) / len(property_counts):.0f}")
print(f"  P50: {sorted(property_counts)[len(property_counts)//2]}")
print(f"  P75: {sorted(property_counts)[int(len(property_counts)*0.75)]}")
print(f"  P95: {sorted(property_counts)[int(len(property_counts)*0.95)]}")
```

---

## Docker Usage

### Build Docker Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY generate_revit_10k_assets.py .

ENTRYPOINT ["python3", "generate_revit_10k_assets.py"]
```

### Run in Docker

```bash
# Build image
docker build -t revit-10k-generator .

# Generate data
docker run -v $(pwd)/output:/app/output revit-10k-generator tenant_revit_10k /app/output
```

---

## Performance Benchmarks

### Generation Time

```
Machine: MacBook Pro M1
Python: 3.11
Time: ~2-3 minutes

Breakdown:
- Asset generation: ~1.5 minutes
- Relationship generation: ~1 minute
- JSON serialization: ~30 seconds
```

### Output Size

```
Assets JSON: ~1.2 GB
Relationships JSON: ~300 MB
Total: ~1.5 GB

Compressed (gzip):
Assets JSON: ~700 MB
Relationships JSON: ~150 MB
Total: ~850 MB
```

### MongoDB Import Time

```
Tool: mongoimport
Workers: 4
Batch Size: 500

Assets: ~2-3 minutes
Relationships: ~1 minute
Total: ~3-4 minutes
```

---

## Troubleshooting

### Out of Memory

If you run out of memory during generation:

1. Reduce asset count in the script
2. Generate in batches
3. Use a machine with more RAM

### Slow Import

If MongoDB import is slow:

1. Increase `--numInsertionWorkers` (4-8)
2. Increase `--batchSize` (500-1000)
3. Check network connectivity
4. Verify MongoDB cluster has sufficient resources

### Validation

Verify generated data:

```bash
# Check JSON validity
python3 -m json.tool output/assets.json > /dev/null && echo "✓ assets.json is valid"
python3 -m json.tool output/relationships.json > /dev/null && echo "✓ relationships.json is valid"

# Check file sizes
ls -lh output/
```

