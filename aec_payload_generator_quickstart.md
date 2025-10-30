# Quick Start Guide - AEC Payload Generator

## 🚀 Get Started in 30 Seconds

### 1. Generate Your First Model

```bash
python3 aec_payload_generator.py
```

**Output**: `aec_output/` directory with 3 files:
- `model.json` - Single model document
- `assets.json` - JSON array with 10,000 assets
- `relationships.json` - JSON array with 2,000 relationships

### 2. Verify the Output

```bash
# Check files created
ls -lh aec_output/

# View model metadata
cat aec_output/model.json

# Count assets and relationships
python3 -c "import json; print(f'Assets: {len(json.load(open(\"aec_output/assets.json\")))}')"
python3 -c "import json; print(f'Relationships: {len(json.load(open(\"aec_output/relationships.json\")))}')"
```

---

## 📊 Common Use Cases

### Small Test Dataset (100 assets)
```bash
python3 aec_payload_generator.py --assets 100 --relationships 20 --output-dir small_test
```

### Medium Dataset (5K assets)
```bash
python3 aec_payload_generator.py --assets 5000 --relationships 1000 --output-dir medium_model
```

### Large Dataset (100K assets)
```bash
python3 aec_payload_generator.py --assets 100000 --relationships 20000 --output-dir large_model
```

### Very Large Dataset (1M assets)
```bash
python3 aec_payload_generator.py --assets 1000000 --relationships 200000 --output-dir million_assets
```

### Reproducible Generation (with seed)
```bash
python3 aec_payload_generator.py --seed 42
```

### Custom Model ID
```bash
python3 aec_payload_generator.py --model-id "building-abc-123" --output-dir building_abc
```

---

## 📁 What Gets Generated

### Asset Types (10,000 total)
- 🧱 **2,300 Walls** - Exterior and interior
- 🚪 **400 Doors** - Single and double
- 🪟 **600 Windows** - Fixed and casement
- 🏢 **850 Rooms** - Various departments
- 🌡️ **2,000 MEP Components** - HVAC, terminals
- 🏗️ **1,150 Structural Elements** - Beams, columns
- 🪑 **2,300 Furniture** - Desks, chairs, tables
- 💡 **400 Fixtures** - Lighting

### Relationships (2,000 total)
- **Hosted**: Doors/windows in walls
- **Room Bounding**: Rooms bounded by walls
- **Serves**: MEP serving rooms
- **Contains**: Rooms containing furniture

---

## 🔍 Inspect the Output

### View Model Metadata
```bash
cat aec_output/model.json | python3 -m json.tool
```

### View First Asset
```bash
python3 -c "import json; assets = json.load(open('aec_output/assets.json')); print(json.dumps(assets[0], indent=2))" | head -40
```

### View First Relationship
```bash
python3 -c "import json; rels = json.load(open('aec_output/relationships.json')); print(json.dumps(rels[0], indent=2))"
```

### Check File Sizes
```bash
ls -lh aec_output/
du -sh aec_output/
```

---

## 📦 Import to MongoDB

### Option 1: Using mongoimport (Command Line)

```bash
cd aec_output

# Import model
mongoimport --db=aec_models --collection=models --file=model.json

# Import assets (note the --jsonArray flag)
mongoimport --db=aec_models --collection=assets --file=assets.json --jsonArray

# Import relationships (note the --jsonArray flag)
mongoimport --db=aec_models --collection=relationships --file=relationships.json --jsonArray
```

### Option 2: Using MongoDB Compass (GUI)

1. Open MongoDB Compass and connect to your database
2. Create three collections: `models`, `assets`, `relationships`
3. For each collection:
   - Click "ADD DATA" → "Import JSON or CSV file"
   - Select the file (`model.json`, `assets.json`, or `relationships.json`)
   - Click "Import"

---

## ✅ Validation Checklist

After generation, verify:

- [ ] Directory created successfully
- [ ] `model.json` exists and is valid JSON
- [ ] `assets.json` exists and contains expected number of documents
- [ ] `relationships.json` exists and contains expected number of documents
- [ ] All files are valid JSON
- [ ] All relationships reference valid asset IDs
- [ ] Total size is reasonable (~2-3KB per asset)

---

## 🎯 Example Workflow

```bash
# 1. Generate a test dataset
python3 aec_payload_generator.py --assets 1000 --relationships 200 --output-dir test_model --seed 123

# 2. Verify it
ls -lh test_model/
cat test_model/model.json

# 3. Import to MongoDB
cd test_model
mongoimport --db=test_db --collection=models --file=model.json
mongoimport --db=test_db --collection=assets --file=assets.json --jsonArray
mongoimport --db=test_db --collection=relationships --file=relationships.json --jsonArray

# 4. Generate production dataset
python3 aec_payload_generator.py --assets 100000 --relationships 20000 --output-dir production --seed 456

# 5. Import to production MongoDB
cd production
mongoimport --uri="mongodb://prod-server:27017" --db=production_db --collection=models --file=model.json
mongoimport --uri="mongodb://prod-server:27017" --db=production_db --collection=assets --file=assets.json --jsonArray
mongoimport --uri="mongodb://prod-server:27017" --db=production_db --collection=relationships --file=relationships.json --jsonArray
```

---

## 📖 Need More Help?

- **Full Documentation**: See `aec_payload_generator_readme.md`
- **Technical Details**: See `aec_payload_generator_summary.md`
- **Architecture Overview**: See `aec_individual_docs_summary.md`
- **Sample Structure**: See `AEC-Sample-Model-10K-Entities-Payload.json`

---

## 🐛 Troubleshooting

### "No module named 'json'"
- **Solution**: Use Python 3.7+ (`python3 --version`)

### Out of memory
- **Solution**: Generate in smaller batches (e.g., `--assets 10000` instead of 1M)

### Directory already exists
- **Solution**: Use a different `--output-dir` or remove the existing directory

### MongoDB import fails
- **Solution**: Ensure MongoDB is running and connection string is correct

### "mongoimport: command not found"
- **Solution**: Install MongoDB tools or use Python import script instead

---

## 💡 Pro Tips

1. **Use seeds for reproducibility**: `--seed 42` generates the same data every time
2. **Start small**: Test with 100 assets before generating 100K+
3. **Use custom model IDs**: `--model-id "project-name"` for better organization
4. **Monitor disk space**: ~2-3KB per asset, so 100K assets = ~250MB
5. **Check relationships**: Ensure relationship count is reasonable (10-20% of assets)
6. **Use --jsonArray flag**: Required when importing JSON arrays with mongoimport
7. **MongoDB Compass**: Great for visual inspection and one-click imports
8. **Multi-tenant**: Use different model IDs to store multiple models in one database

---

## 🎉 You're Ready!

Generate your first model now:

```bash
python3 aec_payload_generator.py
```

Then import to MongoDB:

```bash
cd aec_output
mongoimport --db=aec_models --collection=models --file=model.json
mongoimport --db=aec_models --collection=assets --file=assets.json --jsonArray
mongoimport --db=aec_models --collection=relationships --file=relationships.json --jsonArray
```

Or use MongoDB Compass for a GUI experience!

Happy generating! 🚀

