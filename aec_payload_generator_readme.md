# AEC Payload Generator

A Python generator that creates realistic Autodesk/AutoCAD drawing payloads as MongoDB-ready collection files. Generates 3 JSON files (model, assets, relationships) that can be directly imported into MongoDB using `mongoimport` or MongoDB Compass.

## Features

- **Collection Files**: Single JSON file per collection (model, assets, relationships)
- **Optimized Storage**: Compound `_id` keys eliminate duplicate fields and reduce storage
- **MongoDB Ready**: JSON arrays ready for `mongoimport --jsonArray` or MongoDB Compass
- **Scalable**: Can generate 1M+ assets (limited only by disk space and memory)
- **10,000 Assets**: Generates realistic AEC assets across 8 categories (configurable)
- **2,000 Relationships**: Creates meaningful relationships between assets (configurable)
- **Realistic Distribution**: Matches real-world Revit model patterns
- **Proper Structure**: Follows Autodesk asset graph schema exactly
- **Multi-tenant Support**: Compound keys include modelId for efficient multi-tenant queries
- **Easy Import**: Direct import via mongoimport or MongoDB Compass GUI

## Asset Types Generated

The generator creates assets matching the distribution in the sample file:

| Asset Type | Default Count | Description |
|------------|---------------|-------------|
| Walls | 2,300 | Exterior and interior walls with properties |
| Doors | 400 | Single and double doors with dimensions |
| Windows | 600 | Fixed and casement windows |
| Rooms | 850 | Rooms with occupancy and department info |
| MEP Components | 2,000 | HVAC terminals, diffusers, etc. |
| Structural Elements | 1,150 | Beams, columns, framing |
| Furniture | 2,300 | Desks, chairs, tables |
| Fixtures | 400 | Lighting and electrical fixtures |

**Total: 10,000 assets**

## Relationship Types

The generator creates 2,000 relationships across 4 types:

1. **Hosted** (40%): Doors/windows hosted in walls
2. **Room Bounding** (30%): Rooms bounded by walls
3. **Serves** (20%): MEP components serving rooms
4. **Contains** (10%): Rooms containing furniture/fixtures

## Installation

No external dependencies required! Uses only Python standard library.

```bash
# Requires Python 3.7+
python3 --version
```

## Usage

### Basic Usage (10K assets, 2K relationships)

```bash
python3 aec_payload_generator.py
```

This generates an `aec_output/` directory with 5 files:
- `model.json` - Single model document
- `assets.json` - JSON array with 10,000 assets (for inspection)
- `assets.jsonl` - JSONL format for mongoimport
- `relationships.json` - JSON array with 2,000 relationships (for inspection)
- `relationships.jsonl` - JSONL format for mongoimport

### Custom Configuration

```bash
# Generate 5K assets and 1K relationships
python3 aec_payload_generator.py --assets 5000 --relationships 1000 --output-dir my_model

# Specify custom model ID
python3 aec_payload_generator.py --model-id "building-123" --output-dir building_123

# Use random seed for reproducibility
python3 aec_payload_generator.py --seed 42

# Generate large dataset (100K assets)
python3 aec_payload_generator.py --assets 100000 --relationships 20000 --output-dir large_model
```

### Command Line Options

```
--assets N          Number of assets to generate (default: 10000)
--relationships N   Number of relationships to generate (default: 2000)
--output-dir DIR    Output directory path (default: aec_output)
--model-id ID       Model ID (default: auto-generated timestamp)
--seed N           Random seed for reproducibility
```
### Import to MongoDB

#### Option 1: Using mongoimport (Recommended)

```bash
cd aec_output

# Import model document
mongoimport --db=aec_models --collection=models --file=model.json

# Import assets (JSONL format - one document per line)
mongoimport --db=aec_models --collection=assets --file=assets.jsonl

# Import relationships (JSONL format - one document per line)
mongoimport --db=aec_models --collection=relationships --file=relationships.jsonl
```

**Note**: Use `.jsonl` files for mongoimport (JSONL format, one document per line). No `--jsonArray` flag needed!

#### Option 2: Using MongoDB Compass (GUI)

1. Open MongoDB Compass
2. Connect to your database
3. Create collections: `models`, `assets`, `relationships`
4. For each collection:
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select the corresponding file (`model.json`, `assets.json`, `relationships.json`)
   - MongoDB Compass can handle both JSON arrays and JSONL formats
   - Click "Import"

## Output Structure

### Directory Structure

```
aec_output/
├── model.json                    # Single model document
├── assets.json                   # JSON array with all assets (for inspection)
├── assets.jsonl                  # JSONL format for mongoimport
├── relationships.json            # JSON array with all relationships (for inspection)
└── relationships.jsonl           # JSONL format for mongoimport
```

**Note**: `.jsonl` files are optimized for `mongoimport` (one document per line). `.json` files are formatted for easy inspection.

### Model Document (model.json)

```json
{
  "modelId": "model-20251030-082305",
  "batchId": "batch-aec-model-10000-entities",
  "description": "AEC Model with 10,000 entities - Generated payload",
  "modelStatistics": {
    "totalEntities": 10000,
    "modelSize": "23.10MB",
    "averageAssetSize": "2.37KB",
    "batchCount": 400,
    "entitiesPerBatch": 25
  },
  "entityDistribution": {
    "walls": 2300,
    "doors": 400,
    "windows": 600,
    "rooms": 850,
    "mepComponents": 2000,
    "structuralElements": 1150,
    "furniture": 2300,
    "fixtures": 400
  },
  "generationInfo": {
    "generatedAt": "2025-10-30T08:23:05.622452",
    "generator": "AECPayloadGenerator v2.0",
    "totalAssets": 10000,
    "totalRelationships": 2000,
    "outputFormat": "individual-documents"
  }
}
```

## Asset Structure Example

Each asset document uses a **compound `_id`** for optimization:

- **_id.modelId**: Reference to parent model (for multi-tenant support)
- **_id.id**: Unique identifier within the model (e.g., `wall-000001`)
- **type**: Autodesk type ID (e.g., `autodesk.revit:wall-2.0.0`)
- **space**: Building space reference
- **attributes**: System attributes including uniqueId
- **components**: Metadata, properties, geometry, and custom properties

### Wall Asset Document

```json
{
  "_id": {
    "modelId": "model-20251030-082305",
    "id": "wall-000001"
  },
  "type": "autodesk.revit:wall-2.0.0",
  "space": {"id": "space-building-level-1"},
  "attributes": {
    "system": {
      "uniqueId": "e7d0c1a2-3b4c-5d6e-7f8g-9h0i1j2k3l4m-001"
    }
  },
  "components": {
    "insertions": {
      "metadata": { /* elementId, categoryId, phase */ },
      "wallProperties": { /* familyName, typeName, level */ },
      "geometry": { /* minPoint, maxPoint */ },
      "properties": { /* area, volume, etc. */ }
    }
  }
}
```

**Benefits**: No duplicate `modelId` and `id` fields, natural primary key, ~10% storage reduction

## Relationship Structure Example

Each relationship uses a **compound `_id`** with the relationship endpoints:

### Relationship Document

```json
{
  "_id": {
    "modelId": "model-20251030-082305",
    "fromAssetId": "door-000001",
    "toAssetId": "wall-000001"
  },
  "type": "autodesk.revit:hosted-1.0.0",
  "attributes": {
    "application": {
      "relationshipType": "hosted",
      "insertionPoint": [10.5, 0, 0]
    }
  }
}
```

**Benefits**: No duplicate fields, prevents duplicate relationships, efficient lookups

## MongoDB Collections

After import, your MongoDB database will have three collections:

### models Collection
- One document per model
- Indexed on `modelId` (unique)

### assets Collection
- One document per asset
- Indexed on `(modelId, id)` (unique compound index)
- Indexed on `modelId` for filtering
- Indexed on `type` for querying by asset type

### relationships Collection
- One document per relationship
- Indexed on `(modelId, id)` (unique compound index)
- Indexed on `modelId` for filtering
- Indexed on `from.assetId` for traversal
- Indexed on `to.assetId` for reverse traversal
- Indexed on `type` for querying by relationship type

## Performance

- **Generation Time**: ~5-10 seconds for 10K assets
- **File Size**: ~20-30MB for 10K assets
- **Memory Usage**: ~500MB during generation

## Validation

The generated payload matches the structure of `AEC-Sample-Model-10K-Entities-Payload.json`:

✓ Same JSON schema  
✓ Same asset type distribution  
✓ Same component structure  
✓ Same relationship types  
✓ Realistic property values  
✓ Valid geometry bounds  
✓ Proper type IDs  

## Use Cases

1. **Testing**: Load testing for asset graph systems
2. **Development**: Sample data for development environments
3. **Benchmarking**: Performance testing with realistic data
4. **Demos**: Demonstration data for presentations
5. **Integration**: Testing data pipelines and integrations

## Customization

To modify asset distributions, edit the `ASSET_TYPES` dictionary in `aec_payload_generator.py`:

```python
ASSET_TYPES = {
    'walls': {
        'count': 2300,  # Change this
        'type': 'autodesk.revit:wall-2.0.0',
        # ...
    }
}
```

## Comparison with Sample File

| Metric | Sample File | Generated |
|--------|-------------|-----------|
| Total Assets | 10,000 | 10,000 |
| Relationships | ~5 | 2,000 |
| File Size | 22MB | ~25MB |
| Asset Types | 8 | 8 |
| Schema Version | 2.0.0 | 2.0.0 |

## License

This generator is part of the Autodesk OneGraph project.

## Support

For issues or questions, refer to the main project documentation.

