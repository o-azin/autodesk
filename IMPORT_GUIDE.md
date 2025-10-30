# MongoDB Import Guide

This guide shows you how to import the generated AEC payload files into MongoDB.

## 📁 Generated Files

After running the generator, you'll have 3 files:

```
aec_output/
├── model.json           # Single model document
├── assets.json          # JSON array with all assets
└── relationships.json   # JSON array with all relationships
```

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

# Import assets (note the --jsonArray flag!)
mongoimport --db=aec_models --collection=assets --file=assets.json --jsonArray

# Import relationships (note the --jsonArray flag!)
mongoimport --db=aec_models --collection=relationships --file=relationships.json --jsonArray
```

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
  --file=assets.json \
  --jsonArray

mongoimport --uri="mongodb://username:password@host:port" \
  --db=aec_models \
  --collection=relationships \
  --file=relationships.json \
  --jsonArray
```

#### Important Notes
- **Always use `--jsonArray` flag** for `assets.json` and `relationships.json`
- **Do NOT use `--jsonArray`** for `model.json` (it's a single document)
- The collections will be created automatically if they don't exist

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
   - Select `assets.json`
   - Click "Import"
   - You should see N documents imported (e.g., 10,000)

5. **Create and Import Relationships Collection**
   - Click "Create Collection" → Name it `relationships`
   - Select the `relationships` collection
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select `relationships.json`
   - Click "Import"
   - You should see M documents imported (e.g., 2,000)

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
db.assets.distinct("modelId")
db.relationships.distinct("modelId")
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
    { "from.assetId": "wall-000001" },
    { "to.assetId": "wall-000001" }
  ]
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
db.assets.createIndex({ modelId: 1 })
db.assets.createIndex({ type: 1 })
db.assets.createIndex({ "modelId": 1, "id": 1 }, { unique: true })

// Relationship indexes
db.relationships.createIndex({ modelId: 1 })
db.relationships.createIndex({ type: 1 })
db.relationships.createIndex({ "from.assetId": 1 })
db.relationships.createIndex({ "to.assetId": 1 })
db.relationships.createIndex({ "modelId": 1, "id": 1 }, { unique: true })
```

2. **Multi-tenant Setup**: Use `modelId` to filter queries:
```javascript
// Query assets for specific model
db.assets.find({ modelId: "model-20251030-123456" })
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

