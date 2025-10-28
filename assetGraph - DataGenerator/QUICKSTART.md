# Quick Start Guide

## 30-Second Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd revit-1m-generator

# 2. Generate data (30-60 minutes for 1M+ assets)
python3 generate_revit_1m_assets.py

# 3. Check output
ls -lh output/
```

Done! You now have:
- `output/tenant_0001/` through `output/tenant_0050/`
- Each tenant has `assets.json` and `relationships.json`
- **Total: 1,198,800 assets + 3,596,400 relationships**

---

## What You Get

✅ **1,198,800 realistic Revit assets** across 50 tenants:
- 35 small tenants (17K assets each)
- 12 medium tenants (~27.6K assets each)
- 2 large tenants (~130K assets each)
- 1 enterprise tenant (15.9K assets)
- 8 asset types (walls, doors, MEP, furniture, etc.)
- 100-5,000 properties per asset (realistic distribution)
- Revit metadata (elementId, categoryId, phases)
- 3D geometry bounds

✅ **3,596,400 relationships** with:
- 6 relationship types (hosted, serves, connects, etc.)
- Proper bitemporal structure (validFrom, validTo)
- Tenant and transaction time tracking

✅ **Property distribution matching real Revit data**:
- P50: 287 properties
- P75: 592 properties
- P95: 997 properties
- P99: 4,491 properties

---

## Next Steps

### Option 1: Import to MongoDB

```bash
# 1. Create database
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/"
use tenant_revit_10k

# 2. Import data
mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection assets \
  --file output/assets.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500 \
  --drop

mongoimport \
  --uri "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" \
  --collection relationships \
  --file output/relationships.json \
  --jsonArray \
  --numInsertionWorkers 4 \
  --batchSize 500 \
  --drop

# 3. Create indexes
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/tenant_revit_10k" << 'EOF'
db.assets.createIndex({ assetId: 1, validTo: 1 })
db.assets.createIndex({ spaceId: 1, validTo: 1 })
db.assets.createIndex({ type: 1, validTo: 1 })
db.relationships.createIndex({ fromAssetId: 1, validTo: 1 })
db.relationships.createIndex({ toAssetId: 1, validTo: 1 })
EOF
```

### Option 2: Analyze Data

```bash
python3 << 'EOF'
import json

# Load data
with open('output/assets.json') as f:
    assets = json.load(f)

# Analyze
print(f"Total assets: {len(assets)}")
print(f"Asset types: {len(set(a['type'] for a in assets))}")
print(f"Spaces: {len(set(a['spaceId'] for a in assets))}")

# Property distribution
props = []
for asset in assets:
    try:
        p = asset['components']['insertions']['properties']['staticChildren']['properties']['insertions']
        props.append(len(p))
    except:
        pass

print(f"\nProperty distribution:")
print(f"  Min: {min(props)}")
print(f"  Max: {max(props)}")
print(f"  Avg: {sum(props)//len(props)}")
EOF
```

### Option 3: Customize Generation

Edit `generate_revit_10k_assets.py`:

```python
# Change asset count
for i in range(1, 5001):  # Generate 5K instead of 10K

# Change relationship ratio
for i in range(15000):  # Generate 15K instead of 30K

# Add custom parameters
REVIT_PARAMETERS.append(
    ('customParam', 'autodesk.revit.parameter:custom-1.0.0', 'String', 
     lambda: 'custom_value', None)
)
```

---

## File Structure

```
revit-10k-generator/
├── generate_revit_10k_assets.py    # Main script
├── README.md                        # Full documentation
├── QUICKSTART.md                    # This file
├── EXAMPLES.md                      # Usage examples
├── SCHEMA.md                        # Data schema
├── requirements.txt                 # Dependencies (none!)
├── LICENSE                          # MIT License
├── .gitignore                       # Git ignore rules
└── output/                          # Generated data
    ├── assets.json                  # 10K assets
    └── relationships.json           # 30K relationships
```

---

## Common Commands

```bash
# Generate with custom tenant ID
python3 generate_revit_10k_assets.py tenant_acme

# Generate with custom output directory
python3 generate_revit_10k_assets.py tenant_acme ./data

# Validate JSON
python3 -m json.tool output/assets.json > /dev/null && echo "✓ Valid"

# Check file sizes
du -sh output/*

# Count documents
python3 -c "import json; print(len(json.load(open('output/assets.json'))))"
```

---

## Troubleshooting

### Out of Memory?
- Reduce asset count in script (change `range(1, 10001)`)
- Use a machine with more RAM
- Generate in smaller batches

### Slow Generation?
- Normal! Takes 2-3 minutes
- Check CPU usage: `top` or `Activity Monitor`
- Reduce property count if needed

### MongoDB Import Fails?
- Check connection string
- Verify credentials
- Ensure database exists
- Check network connectivity

### JSON Invalid?
```bash
python3 -m json.tool output/assets.json > /dev/null
```

---

## Performance

| Operation | Time |
|-----------|------|
| Generate 10K assets | ~1.5 min |
| Generate 30K relationships | ~1 min |
| JSON serialization | ~30 sec |
| **Total** | **~2-3 min** |

| Metric | Value |
|--------|-------|
| Assets JSON size | ~1.2 GB |
| Relationships JSON size | ~300 MB |
| Total size | ~1.5 GB |
| Compressed (gzip) | ~850 MB |

---

## Support

- 📖 Read [README.md](README.md) for full documentation
- 📋 Check [EXAMPLES.md](EXAMPLES.md) for usage examples
- 📊 See [SCHEMA.md](SCHEMA.md) for data schema details
- 🐛 Report issues on GitHub

---

## Key Features

✨ **Realistic Data**
- Matches actual Revit workload distribution
- Property counts from real tenant_0001 data
- Authentic Revit metadata and structure

⚡ **Fast Generation**
- 10K assets in 2-3 minutes
- No external dependencies
- Pure Python (3.7+)

🔧 **Easy to Use**
- Single command to generate
- Customizable parameters
- Clear output and statistics

📦 **Production Ready**
- Proper bitemporal schema
- Correct Revit structure
- Ready for MongoDB import

---

Generated: 2025-10-28

