# Multi-Model Generation Guide

## Overview

The AEC Payload Generator now supports generating **multiple models** with their corresponding assets and relationships in the same files. This is perfect for:

- **Multi-tenant testing**: Simulate multiple buildings/projects in one database
- **Large-scale testing**: Generate thousands of models efficiently
- **Realistic scenarios**: Test queries across multiple models
- **Performance testing**: Benchmark multi-model queries and aggregations

## How It Works

When you specify `--models N`, the generator creates:

```
output_dir/
├── models.jsonl         # N model documents (one per line)
├── assets.jsonl         # All assets from all models (one per line)
└── relationships.jsonl  # All relationships from all models (one per line)
```

Each model gets a **unique modelId**, and all assets and relationships reference their parent model via the `_id.modelId` field.

## Usage

### Basic Multi-Model Generation

```bash
# Generate 10 models, each with 1000 assets and 500 relationships
python3 aec_payload_generator.py --models 10 --assets 1000 --relationships 500 --output-dir multi_tenant
```

### Your Use Case: 10K Models

```bash
# Generate 10,000 models, each with 10K assets and 5K relationships
python3 aec_payload_generator.py \
  --models 10000 \
  --assets 10000 \
  --relationships 5000 \
  --output-dir large_multi_model \
  --seed 42
```

**Expected output:**
- `models.jsonl`: ~70 MB (10,000 model documents)
- `assets.jsonl`: ~250 GB (100 million assets)
- `relationships.jsonl`: ~125 GB (50 million relationships)
- **Total**: ~375 GB
- **Generation time**: ~6-8 hours (depending on hardware)

### Smaller Test Example

```bash
# Test with 3 models first
python3 aec_payload_generator.py --models 3 --assets 100 --relationships 50 --output-dir test_multi
```

## File Structure

### models.jsonl
Each line is a complete model document:

```jsonl
{"modelId": "model-20251030-120000-000000", "name": "AEC Model 1", "description": "...", "createdAt": "...", "modelStatistics": {...}, "entityDistribution": {...}}
{"modelId": "model-20251030-120000-000001", "name": "AEC Model 2", "description": "...", "createdAt": "...", "modelStatistics": {...}, "entityDistribution": {...}}
{"modelId": "model-20251030-120000-000002", "name": "AEC Model 3", "description": "...", "createdAt": "...", "modelStatistics": {...}, "entityDistribution": {...}}
```

### assets.jsonl
Each line is an asset document with `_id.modelId` referencing its parent model:

```jsonl
{"_id": {"modelId": "model-20251030-120000-000000", "id": "wall-000001"}, "type": "autodesk.revit:wall-2.0.0", ...}
{"_id": {"modelId": "model-20251030-120000-000000", "id": "wall-000002"}, "type": "autodesk.revit:wall-2.0.0", ...}
{"_id": {"modelId": "model-20251030-120000-000001", "id": "wall-000001"}, "type": "autodesk.revit:wall-2.0.0", ...}
```

### relationships.jsonl
Each line is a relationship document with `_id.modelId` referencing its parent model:

```jsonl
{"_id": {"modelId": "model-20251030-120000-000000", "id": "rel-hosted-000001", "fromAssetId": "door-001", "toAssetId": "wall-001"}, "type": "autodesk.revit:hosted-1.0.0", ...}
{"_id": {"modelId": "model-20251030-120000-000001", "id": "rel-hosted-000001", "fromAssetId": "door-001", "toAssetId": "wall-001"}, "type": "autodesk.revit:hosted-1.0.0", ...}
```

## Import to MongoDB

```bash
cd output_dir

# Import all models
mongoimport --db=multi_tenant --collection=models --file=models.jsonl

# Import all assets
mongoimport --db=multi_tenant --collection=assets --file=assets.jsonl

# Import all relationships
mongoimport --db=multi_tenant --collection=relationships --file=relationships.jsonl
```

**Note**: No `--jsonArray` flag needed for JSONL files!

## Querying Multi-Model Data

### Count models
```javascript
db.models.countDocuments()
// Returns: 10000
```

### Count total assets
```javascript
db.assets.countDocuments()
// Returns: 100,000,000 (10K models × 10K assets)
```

### Get assets for a specific model
```javascript
db.assets.find({ "_id.modelId": "model-20251030-120000-000000" })
```

### Count assets per model
```javascript
db.assets.aggregate([
  { $group: { _id: "$_id.modelId", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Find all models with more than 5000 walls
```javascript
db.assets.aggregate([
  { $match: { type: "autodesk.revit:wall-2.0.0" } },
  { $group: { _id: "$_id.modelId", wallCount: { $sum: 1 } } },
  { $match: { wallCount: { $gt: 5000 } } }
])
```

### Get relationships across all models
```javascript
db.relationships.aggregate([
  { $group: { _id: "$type", count: { $sum: 1 } } }
])
```

## Performance Considerations

### Memory Usage
- **Generation**: ~500 MB per model during generation
- **Import**: MongoDB will use ~2-3x the file size during import

### Disk Space
For 10K models with 10K assets each:
- **Generation**: ~375 GB
- **MongoDB storage**: ~450-500 GB (with indexes)
- **Total needed**: ~850 GB free space

### Generation Time
| Models | Assets/Model | Total Assets | Est. Time |
|--------|--------------|--------------|-----------|
| 10 | 1,000 | 10K | ~10 seconds |
| 100 | 1,000 | 100K | ~2 minutes |
| 1,000 | 1,000 | 1M | ~20 minutes |
| 10,000 | 1,000 | 10M | ~3 hours |
| 10,000 | 10,000 | 100M | ~6-8 hours |

### Import Time
| Total Assets | Import Time |
|--------------|-------------|
| 100K | ~30 seconds |
| 1M | ~5 minutes |
| 10M | ~45 minutes |
| 100M | ~6-8 hours |

## Recommended Indexes

For multi-model queries, create these indexes:

```javascript
// Model indexes
db.models.createIndex({ modelId: 1 })

// Asset indexes
db.assets.createIndex({ "_id.modelId": 1 })
db.assets.createIndex({ "_id.modelId": 1, type: 1 })
db.assets.createIndex({ type: 1 })

// Relationship indexes
db.relationships.createIndex({ "_id.modelId": 1 })
db.relationships.createIndex({ "_id.modelId": 1, type: 1 })
db.relationships.createIndex({ "_id.fromAssetId": 1 })
db.relationships.createIndex({ "_id.toAssetId": 1 })
db.relationships.createIndex({ type: 1 })
```

## Best Practices

1. **Start Small**: Test with 10 models first, then scale up
2. **Use Seeds**: Use `--seed` for reproducible datasets
3. **Monitor Disk Space**: Ensure you have 2-3x the expected file size available
4. **Batch Imports**: For very large datasets, consider importing in batches
5. **Index After Import**: Create indexes after importing all data for better performance

## Example Workflow

```bash
# 1. Test with small dataset
python3 aec_payload_generator.py --models 10 --assets 100 --relationships 50 --output-dir test_multi --seed 42

# 2. Import and verify
cd test_multi
mongoimport --db=test_db --collection=models --file=models.jsonl
mongoimport --db=test_db --collection=assets --file=assets.jsonl
mongoimport --db=test_db --collection=relationships --file=relationships.jsonl

# 3. Verify counts
mongo test_db --eval "db.models.countDocuments()"
mongo test_db --eval "db.assets.countDocuments()"
mongo test_db --eval "db.relationships.countDocuments()"

# 4. If successful, generate full dataset
python3 aec_payload_generator.py --models 10000 --assets 10000 --relationships 5000 --output-dir production_multi --seed 42
```

## Comparison: Single vs Multi-Model

| Feature | Single Model | Multi-Model |
|---------|--------------|-------------|
| Files | 3 files (model.json, assets.json/jsonl, relationships.json/jsonl) | 3 files (models.jsonl, assets.jsonl, relationships.jsonl) |
| Model count | 1 | N (configurable) |
| Assets per file | All from 1 model | All from N models |
| Import | 3 imports | 3 imports |
| Use case | Single building/project | Multi-tenant, large-scale testing |
| Query complexity | Simple | Requires filtering by modelId |

## Summary

✅ **Generate multiple models in one command**  
✅ **All data in 3 JSONL files**  
✅ **Each model has unique ID**  
✅ **Assets and relationships reference their parent model**  
✅ **Perfect for multi-tenant testing**  
✅ **Scales to millions of assets**  

For your use case of **10K models with 10K assets each**, the command is:

```bash
python3 aec_payload_generator.py --models 10000 --assets 10000 --relationships 5000 --output-dir large_multi_model --seed 42
```

This will generate **100 million assets** and **50 million relationships** across **10,000 models**! 🚀

