# AEC Payload Generator - Complete Guide

## 📋 Overview

The AEC Payload Generator creates realistic Autodesk/AutoCAD drawing payloads as **MongoDB-ready collection files**. Generates 3 JSON files (model, assets, relationships) that can be directly imported into MongoDB using `mongoimport` or MongoDB Compass.

## 🚀 Quick Start

```bash
# Generate 10K assets and 2K relationships
python3 aec_payload_generator.py

# Import to MongoDB
cd aec_output
mongoimport --db=aec_models --collection=models --file=model.json
mongoimport --db=aec_models --collection=assets --file=assets.json --jsonArray
mongoimport --db=aec_models --collection=relationships --file=relationships.json --jsonArray
```

## 📁 Project Files

### Core Generator
- **`aec_payload_generator.py`** (767 lines)
  - Main generator script
  - Creates 3 JSON files: model, assets, relationships
  - Configurable via CLI arguments
  - Generates 8 asset types with realistic properties
  - Assets and relationships stored as JSON arrays

### Validation (Optional)
- **`aec_payload_validator.py`** (175 lines)
  - Validation tool for old single-file format
  - Can be used to validate structure

### Documentation
- **`aec_payload_generator_readme.md`**
  - Comprehensive documentation
  - Usage examples
  - Output structure
  - Asset and relationship schemas

- **`aec_payload_generator_quickstart.md`**
  - Quick start guide
  - Common use cases
  - Example workflows
  - Troubleshooting tips

- **`aec_payload_generator_summary.md`**
  - Technical implementation details
  - Asset type distributions
  - Property specifications

- **`aec_individual_docs_summary.md`**
  - Architecture overview
  - Migration guide from v1.0
  - Performance benchmarks
  - MongoDB best practices

- **`README_AEC_GENERATOR.md`** (this file)
  - Complete project overview
  - File listing and descriptions

### Sample Data
- **`AEC-Sample-Model-10K-Entities-Payload.json`**
  - Original sample file (reference structure)
  - Single-file format (legacy)

## 🏗️ Architecture

### Current - Collection Files

```
aec_output/
├── model.json                    # Single model document
├── assets.json                   # JSON array with all assets
└── relationships.json            # JSON array with all relationships
```

**Benefits:**
- ✅ Simple structure - 3 files total
- ✅ Direct import with mongoimport --jsonArray
- ✅ Easy to inspect and validate
- ✅ Works with MongoDB Compass GUI
- ✅ Multi-tenant support via `modelId` field in each document
- ✅ Can generate 100K+ assets (limited by memory)

### Legacy - Single Payload File

```json
{
  "batchId": "...",
  "commands": [{"assets": [...]}],
  "relationships": [...]
}
```

**Limitations:**
- ❌ Limited to ~10K assets before hitting MongoDB 16MB size limit
- ❌ Cannot import directly to MongoDB
- ❌ Difficult to work with

## 📊 Asset Types

The generator creates 8 realistic asset types:

| Type | Default % | Description |
|------|-----------|-------------|
| Walls | 23% | Exterior/interior with area, volume |
| Doors | 4% | Single/double with dimensions |
| Windows | 6% | Fixed/casement with sizing |
| Rooms | 8.5% | With departments and occupancy |
| MEP Components | 20% | HVAC terminals and diffusers |
| Structural Elements | 11.5% | Beams and columns |
| Furniture | 23% | Desks, chairs, tables |
| Fixtures | 4% | Lighting fixtures |

## 🔗 Relationship Types

- **Hosted** (~40%): Doors/windows in walls with insertion points
- **Room Bounding** (~30%): Rooms bounded by walls
- **Serves** (~20%): MEP components serving rooms
- **Contains** (~10%): Rooms containing furniture/fixtures

## 💻 Usage Examples

### Basic Generation

```bash
# Default: 10K assets, 2K relationships
python3 aec_payload_generator.py

# Custom counts
python3 aec_payload_generator.py --assets 100000 --relationships 20000

# Custom output directory
python3 aec_payload_generator.py --output-dir my_model

# Custom model ID
python3 aec_payload_generator.py --model-id "building-123"

# Reproducible with seed
python3 aec_payload_generator.py --seed 42
```

### Import to MongoDB

**Option 1: mongoimport (Command Line)**
```bash
cd aec_output

# Import model
mongoimport --db=aec_models --collection=models --file=model.json

# Import assets (note --jsonArray flag)
mongoimport --db=aec_models --collection=assets --file=assets.json --jsonArray

# Import relationships (note --jsonArray flag)
mongoimport --db=aec_models --collection=relationships --file=relationships.json --jsonArray
```

**Option 2: MongoDB Compass (GUI)**
1. Open MongoDB Compass and connect
2. Create collections: `models`, `assets`, `relationships`
3. For each collection, click "ADD DATA" → "Import JSON or CSV file"
4. Select the corresponding file and click "Import"

## 📈 Performance

### Generation Performance
- **100 assets**: <1 second
- **1K assets**: ~1 second
- **10K assets**: ~5 seconds
- **100K assets**: ~45 seconds
- **1M assets**: ~7-8 minutes

### File Sizes
- **Model document**: ~1KB
- **10K assets**: ~25MB (assets.json)
- **2K relationships**: ~700KB (relationships.json)
- **100K assets**: ~250MB (assets.json)
- **20K relationships**: ~7MB (relationships.json)

### MongoDB Import Performance
- **10K assets**: ~2-3 seconds with mongoimport
- **100K assets**: ~20-30 seconds with mongoimport
- **Import via Compass**: Slightly slower but more visual feedback

## 🗄️ MongoDB Collections

After import, three collections are created:

### models Collection
```javascript
{
  modelId: "model-20251030-082305",
  batchId: "batch-aec-model-10000-entities",
  description: "AEC Model with 10,000 entities",
  modelStatistics: { ... },
  entityDistribution: { ... },
  generationInfo: { ... }
}
```
**Indexes:** `modelId` (unique)

### assets Collection
```javascript
{
  modelId: "model-20251030-082305",
  id: "wall-000001",
  type: "autodesk.revit:wall-2.0.0",
  space: { id: "space-building-level-1" },
  attributes: { ... },
  components: { ... }
}
```
**Indexes:** `(modelId, id)` (unique), `modelId`, `type`

### relationships Collection
```javascript
{
  modelId: "model-20251030-082305",
  id: "rel-hosted-000001",
  type: "autodesk.revit:hosted-1.0.0",
  from: { assetId: "door-000001" },
  to: { assetId: "wall-000001" },
  attributes: { ... }
}
```
**Indexes:** `(modelId, id)` (unique), `modelId`, `from.assetId`, `to.assetId`, `type`

## 🔍 Sample MongoDB Queries

```javascript
// Get model information
db.models.findOne({modelId: "model-20251030-082305"})

// Count assets by type
db.assets.aggregate([
  { $match: { modelId: "model-20251030-082305" } },
  { $group: { _id: "$type", count: { $sum: 1 } } }
])

// Find all walls
db.assets.find({
  modelId: "model-20251030-082305",
  type: "autodesk.revit:wall-2.0.0"
})

// Find all doors in walls
db.relationships.find({
  modelId: "model-20251030-082305",
  type: "autodesk.revit:hosted-1.0.0",
  "from.assetId": { $regex: "^door-" }
})

// Find what's connected to a specific asset
db.relationships.find({
  modelId: "model-20251030-082305",
  $or: [
    { "from.assetId": "wall-000001" },
    { "to.assetId": "wall-000001" }
  ]
})
```

## 🛠️ Requirements

- **Python**: 3.7+
- **Dependencies**: None (for generation)
- **Optional**: `pymongo` (for Python-based MongoDB import)
- **Optional**: MongoDB tools (for `mongoimport`)

## 📚 Documentation

1. **Start here**: `aec_payload_generator_quickstart.md`
2. **Full details**: `aec_payload_generator_readme.md`
3. **Architecture**: `aec_individual_docs_summary.md`
4. **Technical specs**: `aec_payload_generator_summary.md`

## 🎯 Use Cases

- **Testing**: Generate realistic test data for AEC applications
- **Development**: Populate development databases
- **Benchmarking**: Test performance with large datasets
- **Demos**: Create impressive demonstrations
- **Training**: Learn MongoDB with realistic data

## 🔄 Migration from v1.0

See `aec_individual_docs_summary.md` for migration guide from single-file format.

## 📝 License

This is a data generator tool for testing and development purposes.

## 🤝 Contributing

Potential enhancements:
- Update validator for individual documents architecture
- Add batch processing for very large datasets
- Add compression support
- Add more asset types
- Add graph traversal utilities

---

**Happy Generating! 🚀**

