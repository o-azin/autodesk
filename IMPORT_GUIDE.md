# MongoDB Import Guide

This guide shows you how to import the generated AEC payload files into MongoDB.

## 📁 Generated Files

After running the generator, you'll have 5 files:

```
aec_output/
├── model.json           # Single model document
├── assets.json          # JSON array with all assets (for inspection)
├── assets.jsonl         # JSONL format for mongoimport (optimized _id)
├── relationships.json   # JSON array with all relationships (for inspection)
└── relationships.jsonl  # JSONL format for mongoimport (optimized _id)
```

**Note**: The `.json` files are formatted JSON arrays for easy inspection. The `.jsonl` files are JSONL format (one document per line) optimized for `mongoimport`.

## 🎯 Optimized Document Structure

### Assets
Each asset uses a **compound `_id`** instead of MongoDB's default ObjectId:
```json
{
  "_id": {
    "modelId": "model-20251030-123456",
    "id": "wall-000001"
  },
  "type": "autodesk.revit:wall-2.0.0",
  "space": {...},
  "attributes": {...},
  "components": {...}
}
```
**Benefits**: No duplicate `modelId` and `id` fields, natural primary key, better query performance

### Relationships
Each relationship uses a **compound `_id`** with the relationship endpoints:
```json
{
  "_id": {
    "modelId": "model-20251030-123456",
    "fromAssetId": "door-000001",
    "toAssetId": "wall-000001"
  },
  "type": "autodesk.revit:hosted-1.0.0",
  "attributes": {...}
}
```
**Benefits**: No duplicate fields, prevents duplicate relationships, efficient lookups

## 🚀 Import Methods

### Method 1: mongoimport (Command Line) - Recommended

This is the fastest and most reliable method.

#### Prerequisites
- MongoDB tools installed (`mongoimport` command available)
- MongoDB server running

#### Steps

```bash
# Navigate to output directory
cd aec_output

# Import model document
mongoimport --db=aec_models --collection=models --file=model.json

# Import assets (JSONL format - one document per line)
mongoimport --db=aec_models --collection=assets --file=assets.jsonl

# Import relationships (JSONL format - one document per line)
mongoimport --db=aec_models --collection=relationships --file=relationships.jsonl
```

**Why JSONL?** MongoDB's `mongoimport` handles JSONL format (one JSON document per line) better than JSON arrays, especially with compound `_id` fields. No `--jsonArray` flag needed!

#### With Custom MongoDB URI

```bash
# For remote MongoDB or custom connection string
mongoimport --uri="mongodb://username:password@host:port" \
  --db=aec_models \
  --collection=models \
  --file=model.json

mongoimport --uri="mongodb://username:password@host:port" \
  --db=aec_models \
  --collection=assets \
  --file=assets.jsonl

mongoimport --uri="mongodb://username:password@host:port" \
  --db=aec_models \
  --collection=relationships \
  --file=relationships.jsonl
```

#### Important Notes
- **Use `.jsonl` files** for `assets` and `relationships` (JSONL format, one document per line)
- **No `--jsonArray` flag needed** for JSONL files
- **Do NOT use `--jsonArray`** for `model.json` (it's a single document)
- The collections will be created automatically if they don't exist
- The `.json` files are provided for inspection/debugging only

---

### Method 2: MongoDB Compass (GUI) - Easiest

This method is great for beginners or visual learners.

#### Prerequisites
- MongoDB Compass installed
- MongoDB server running

#### Steps

1. **Open MongoDB Compass** and connect to your database

2. **Create Database** (if it doesn't exist)
   - Click "Create Database"
   - Database name: `aec_models`
   - Collection name: `models`

3. **Import Model Document**
   - Select the `models` collection
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select `model.json`
   - Click "Import"
   - You should see 1 document imported

4. **Create and Import Assets Collection**
   - Click "Create Collection" → Name it `assets`
   - Select the `assets` collection
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select `assets.json` (MongoDB Compass can handle JSON arrays)
   - Click "Import"
   - You should see N documents imported (e.g., 10,000)

5. **Create and Import Relationships Collection**
   - Click "Create Collection" → Name it `relationships`
   - Select the `relationships` collection
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select `relationships.json` (MongoDB Compass can handle JSON arrays)
   - Click "Import"
   - You should see M documents imported (e.g., 2,000)

**Note**: MongoDB Compass can import both `.json` (array) and `.jsonl` formats. Use whichever you prefer!

---

## ✅ Verify Import

After importing, verify the data:

### Using MongoDB Shell

```javascript
// Connect to database
use aec_models

// Count documents
db.models.countDocuments()        // Should be 1
db.assets.countDocuments()        // Should be 10000 (or your count)
db.relationships.countDocuments() // Should be 2000 (or your count)

// View model
db.models.findOne()

// View sample asset
db.assets.findOne()

// View sample relationship
db.relationships.findOne()

// Check modelId consistency
db.models.distinct("modelId")
db.assets.distinct("_id.modelId")
db.relationships.distinct("_id.modelId")
// All three should return the same modelId
```

### Using MongoDB Compass

1. Select each collection
2. Check the document count at the top
3. Browse through documents to verify structure

---

## 🔍 Sample Queries

Once imported, try these queries:

### Find all walls
```javascript
db.assets.find({ type: "autodesk.revit:wall-2.0.0" })
```

### Count assets by type
```javascript
db.assets.aggregate([
  { $group: { _id: "$type", count: { $sum: 1 } } }
])
```

### Find all hosted relationships (doors in walls)
```javascript
db.relationships.find({
  type: "autodesk.revit:hosted-1.0.0"
})
```

### Find what's connected to a specific asset
```javascript
db.relationships.find({
  $or: [
    { "_id.fromAssetId": "wall-000001" },
    { "_id.toAssetId": "wall-000001" }
  ]
})
```

### Find a specific asset by modelId and id
```javascript
db.assets.findOne({
  "_id": {
    "modelId": "model-20251030-123456",
    "id": "wall-000001"
  }
})
```

### Get model statistics
```javascript
db.models.findOne({}, { modelStatistics: 1, entityDistribution: 1 })
```

---

## 🎯 Best Practices

1. **Create Indexes** for better query performance:
```javascript
// Asset indexes
db.assets.createIndex({ "_id.modelId": 1 })
db.assets.createIndex({ type: 1 })
db.assets.createIndex({ "_id.modelId": 1, type: 1 })

// Relationship indexes
db.relationships.createIndex({ "_id.modelId": 1 })
db.relationships.createIndex({ type: 1 })
db.relationships.createIndex({ "_id.fromAssetId": 1 })
db.relationships.createIndex({ "_id.toAssetId": 1 })
db.relationships.createIndex({ "_id.modelId": 1, type: 1 })
```

**Note**: The compound `_id` is automatically indexed, so you don't need to create a separate unique index!

2. **Multi-tenant Setup**: Use `_id.modelId` to filter queries:
```javascript
// Query assets for specific model
db.assets.find({ "_id.modelId": "model-20251030-123456" })

// Query relationships for specific model
db.relationships.find({ "_id.modelId": "model-20251030-123456" })
```

3. **Backup Before Import**: Always backup your database before importing large datasets

4. **Test with Small Dataset**: Generate and import 100 assets first to verify everything works

---

## 🐛 Troubleshooting

### Error: "mongoimport: command not found"
**Solution**: Install MongoDB Database Tools
- Download from: https://www.mongodb.com/try/download/database-tools
- Or use Homebrew: `brew install mongodb-database-tools`

### Error: "Failed to parse JSON array"
**Solution**: Make sure you're using the `--jsonArray` flag for assets.json and relationships.json

### Error: "Connection refused"
**Solution**: Make sure MongoDB server is running
- Start MongoDB: `mongod` or `brew services start mongodb-community`

### Import is very slow
**Solution**: 
- Use `mongoimport` instead of Compass for large datasets
- Ensure MongoDB has enough memory
- Consider importing in batches for very large datasets (1M+ assets)

### Duplicate key error
**Solution**: The data was already imported. Either:
- Drop the collections and re-import
- Use `--mode=upsert` flag with mongoimport

---

## 📚 Additional Resources

- [MongoDB Import/Export Documentation](https://docs.mongodb.com/database-tools/mongoimport/)
- [MongoDB Compass Documentation](https://docs.mongodb.com/compass/)
- [MongoDB Query Documentation](https://docs.mongodb.com/manual/tutorial/query-documents/)

---

**Happy Importing! 🎉**

