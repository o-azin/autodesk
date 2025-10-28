# Revit 10K Generator - Complete Index

## 📁 Repository Structure

```
revit-10k-generator/
├── generate_revit_10k_assets.py    # Main generation script
├── README.md                        # Full documentation
├── QUICKSTART.md                    # 30-second quick start
├── EXAMPLES.md                      # Usage examples & MongoDB import
├── SCHEMA.md                        # Data schema documentation
├── INDEX.md                         # This file
├── requirements.txt                 # Dependencies (none!)
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
└── output/                          # Generated data (not in repo)
    ├── assets.json                  # 10K assets (~771 MB)
    └── relationships.json           # 30K relationships (~10 MB)
```

---

## 📖 Documentation Files

### 1. **README.md** - Start Here
Complete documentation covering:
- Overview and features
- Quick start instructions
- Data schema explanation
- Asset types and distribution
- Property types and distribution
- Relationship types
- Performance metrics
- MongoDB import instructions
- Customization guide
- Requirements and support

**Read this first for full understanding.**

### 2. **QUICKSTART.md** - 30-Second Setup
Fast-track guide with:
- 30-second setup instructions
- What you get
- Next steps (3 options)
- File structure
- Common commands
- Troubleshooting
- Performance metrics

**Read this if you want to get started immediately.**

### 3. **EXAMPLES.md** - Practical Usage
Real-world examples including:
- Basic generation commands
- MongoDB import with mongoimport
- Index creation
- Verification queries
- Python usage examples
- Docker usage
- Performance benchmarks
- Troubleshooting guide

**Read this for practical implementation.**

### 4. **SCHEMA.md** - Data Structure
Detailed schema documentation:
- Asset document schema
- Relationship document schema
- Bitemporal pattern explanation
- Recommended indexes
- Data types reference
- Statistics and distribution

**Read this to understand the data structure.**

### 5. **INDEX.md** - This File
Navigation guide for the repository.

---

## 🚀 Quick Navigation

### I want to...

**Generate data quickly**
→ Read [QUICKSTART.md](QUICKSTART.md)

**Understand the full system**
→ Read [README.md](README.md)

**See practical examples**
→ Read [EXAMPLES.md](EXAMPLES.md)

**Understand the data schema**
→ Read [SCHEMA.md](SCHEMA.md)

**Import to MongoDB**
→ See [EXAMPLES.md](EXAMPLES.md) → MongoDB Import section

**Customize the generator**
→ See [README.md](README.md) → Customization section

**Troubleshoot issues**
→ See [QUICKSTART.md](QUICKSTART.md) → Troubleshooting section

---

## 🎯 Main Script: generate_revit_10k_assets.py

### Purpose
Generate 10,000 realistic Revit assets with properties matching real Revit workload distribution.

### Key Features
- ✅ 10,000 assets with realistic structure
- ✅ 30,000 relationships (3:1 ratio)
- ✅ Property distribution: P50: 287, P75: 592, P95: 997, P99: 4491
- ✅ 8 asset types matching Revit categories
- ✅ Revit metadata (elementId, categoryId, phases)
- ✅ 3D geometry bounds
- ✅ Bitemporal schema (validFrom, validTo, transactionTime)

### Usage

```bash
# Default (tenant_revit_10k, output/ directory)
python3 generate_revit_10k_assets.py

# Custom tenant ID
python3 generate_revit_10k_assets.py tenant_acme

# Custom output directory
python3 generate_revit_10k_assets.py tenant_acme ./data
```

### Output
- `assets.json` - 10,000 Revit assets (~771 MB)
- `relationships.json` - 30,000 relationships (~10 MB)

### Performance
- Generation time: 2-3 minutes
- Total output size: ~781 MB
- Compressed (gzip): ~850 MB

---

## 📊 Data Generated

### Assets: 10,000
- **8 asset types** with realistic distribution
- **100-5,000 properties** per asset
- **Revit metadata** (elementId, categoryId, phases)
- **3D geometry** bounds (minPoint, maxPoint)
- **Bitemporal structure** (validFrom, validTo, transactionTime)

### Relationships: 30,000
- **3:1 asset-to-relationship ratio**
- **6 relationship types** (hosted, roomBounding, serves, connects, contains, supports)
- **Proper linking** between assets
- **Bitemporal structure** (validFrom, validTo, transactionTime)

### Property Distribution
Matches real Revit data from tenant_0001:
- **P50**: 287 properties (50% of assets)
- **P75**: 592 properties (75% of assets)
- **P95**: 997 properties (95% of assets)
- **P99**: 4,491 properties (99% of assets)

### Asset Types
| Type | Percentage |
|------|-----------|
| Wall | 23% |
| MEP Component | 20% |
| Furniture | 23% |
| Structural | 11.5% |
| Room | 8.5% |
| Window | 6% |
| Door | 4% |
| Fixture | 4% |

---

## 🔧 Key Functions

### generate_asset()
Creates a single realistic Revit asset with:
- Unique assetId and revisionId
- Bitemporal fields (validFrom, validTo, transactionTime)
- Revit metadata (elementId, categoryId, phases)
- 3D geometry bounds
- 100-5,000 properties with realistic distribution

### generate_relationship()
Creates a single relationship with:
- Unique relationshipId
- fromAssetId and toAssetId
- Random relationship type
- Bitemporal fields

### get_property_count()
Generates property count based on realistic distribution:
- P50: 114-287 properties
- P75: 287-592 properties
- P95: 592-997 properties
- P99: 997-4491 properties

### generate_properties()
Creates realistic Revit parameters:
- height, width, depth (Float64 with units)
- area, volume (Float64 with units)
- mark, comments, description (String)
- fireRating, material (String)

---

## 📋 Workflow

### 1. Generate Data
```bash
python3 generate_revit_10k_assets.py
```

### 2. Verify Output
```bash
ls -lh output/
python3 -m json.tool output/assets.json > /dev/null
```

### 3. Import to MongoDB
```bash
mongoimport --uri "mongodb+srv://..." --collection assets --file output/assets.json --jsonArray
mongoimport --uri "mongodb+srv://..." --collection relationships --file output/relationships.json --jsonArray
```

### 4. Create Indexes
```bash
mongosh "mongodb+srv://..."
db.assets.createIndex({ assetId: 1, validTo: 1 })
db.relationships.createIndex({ fromAssetId: 1, validTo: 1 })
```

### 5. Query Data
```bash
db.assets.findOne()
db.relationships.findOne()
db.assets.countDocuments()
```

---

## 🎓 Learning Path

1. **Start**: Read [QUICKSTART.md](QUICKSTART.md) (5 min)
2. **Understand**: Read [README.md](README.md) (15 min)
3. **Learn Schema**: Read [SCHEMA.md](SCHEMA.md) (10 min)
4. **See Examples**: Read [EXAMPLES.md](EXAMPLES.md) (10 min)
5. **Generate**: Run `python3 generate_revit_10k_assets.py` (3 min)
6. **Import**: Follow MongoDB import in [EXAMPLES.md](EXAMPLES.md) (5 min)
7. **Query**: Test queries in MongoDB (5 min)

**Total time: ~50 minutes**

---

## ✅ Verification Checklist

- [ ] Python 3.7+ installed
- [ ] Script runs without errors
- [ ] assets.json generated (~771 MB)
- [ ] relationships.json generated (~10 MB)
- [ ] JSON files are valid
- [ ] Property distribution matches expected
- [ ] Asset types are correct
- [ ] MongoDB connection works
- [ ] Data imported successfully
- [ ] Indexes created
- [ ] Queries return results

---

## 🐛 Troubleshooting

### Script fails to run
- Check Python version: `python3 --version` (need 3.7+)
- Check file permissions: `chmod +x generate_revit_10k_assets.py`
- Check working directory: `pwd`

### Out of memory
- Reduce asset count in script
- Use machine with more RAM
- Generate in smaller batches

### MongoDB import fails
- Check connection string
- Verify credentials
- Ensure database exists
- Check network connectivity

### JSON validation fails
```bash
python3 -m json.tool output/assets.json > /dev/null
```

---

## 📞 Support

- 📖 Full documentation: [README.md](README.md)
- 🚀 Quick start: [QUICKSTART.md](QUICKSTART.md)
- 📋 Examples: [EXAMPLES.md](EXAMPLES.md)
- 📊 Schema: [SCHEMA.md](SCHEMA.md)
- 🐛 Issues: GitHub Issues

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 🔗 Related Resources

- [Autodesk Revit API](https://www.autodesk.com/developer/revit)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Revit Data Model](https://www.autodesk.com/)

---

## 📈 Statistics

### Generated Data
- **Total Assets**: 10,000
- **Total Relationships**: 30,000
- **Asset Types**: 8
- **Spaces**: 5
- **Relationship Types**: 6

### File Sizes
- **assets.json**: ~771 MB
- **relationships.json**: ~10 MB
- **Total**: ~781 MB
- **Compressed (gzip)**: ~850 MB

### Performance
- **Generation Time**: 2-3 minutes
- **MongoDB Import Time**: 3-4 minutes
- **Total Setup Time**: ~10 minutes

---

Generated: 2025-10-28

