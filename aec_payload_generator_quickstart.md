# Quick Start Guide - AEC Payload Generator

## 🚀 Get Started in 30 Seconds

### 1. Generate Your First Payload

```bash
python3 aec_payload_generator.py
```

**Output**: `aec_generated_payload.json` with 10,000 assets and 2,000 relationships

### 2. Validate the Output

```bash
python3 validate_payload.py aec_generated_payload.json
```

**Result**: Detailed validation report showing structure, statistics, and distribution

---

## 📊 Common Use Cases

### Small Test Dataset (100 assets)
```bash
python3 aec_payload_generator.py --assets 100 --relationships 20 --output small_test.json
```

### Medium Dataset (5K assets)
```bash
python3 aec_payload_generator.py --assets 5000 --relationships 1000 --output medium_model.json
```

### Large Dataset (20K assets)
```bash
python3 aec_payload_generator.py --assets 20000 --relationships 5000 --output large_model.json
```

### Reproducible Generation (with seed)
```bash
python3 aec_payload_generator.py --seed 42
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

### View Statistics
```bash
python3 -c "import json; d=json.load(open('aec_generated_payload.json')); print(json.dumps(d['modelStatistics'], indent=2))"
```

### View Entity Distribution
```bash
python3 -c "import json; d=json.load(open('aec_generated_payload.json')); print(json.dumps(d['entityDistribution'], indent=2))"
```

### Count Relationships by Type
```bash
python3 -c "import json; d=json.load(open('aec_generated_payload.json')); rels=d['relationships']; types={}; [types.update({r['attributes']['application']['relationshipType']: types.get(r['attributes']['application']['relationshipType'], 0)+1}) for r in rels]; print(json.dumps(types, indent=2))"
```

---

## ✅ Validation Checklist

After generation, verify:

- [ ] File created successfully
- [ ] File size is reasonable (~2-3KB per asset)
- [ ] Total assets matches requested count
- [ ] All 8 asset types present
- [ ] Relationships reference valid asset IDs
- [ ] JSON is valid and well-formed

Run validation:
```bash
python3 validate_payload.py aec_generated_payload.json
```

---

## 🎯 Example Workflow

```bash
# 1. Generate a test dataset
python3 aec_payload_generator.py --assets 1000 --relationships 200 --output test.json --seed 123

# 2. Validate it
python3 validate_payload.py test.json

# 3. Generate production dataset
python3 aec_payload_generator.py --seed 456

# 4. Validate production dataset
python3 validate_payload.py aec_generated_payload.json

# 5. Compare test vs production
python3 validate_payload.py test.json --compare aec_generated_payload.json
```

---

## 📖 Need More Help?

- **Full Documentation**: See `AEC_GENERATOR_README.md`
- **Technical Details**: See `GENERATOR_SUMMARY.md`
- **Sample Structure**: See `AEC-Sample-Model-10K-Entities-Payload.json`

---

## 🐛 Troubleshooting

### "No module named 'json'"
- **Solution**: Use Python 3.7+ (`python3 --version`)

### File too large
- **Solution**: Reduce asset count (`--assets 1000`)

### Out of memory
- **Solution**: Generate in smaller batches or increase system memory

### Invalid JSON
- **Solution**: Check file wasn't truncated, re-generate with `--seed` for consistency

---

## 💡 Pro Tips

1. **Use seeds for reproducibility**: `--seed 42` generates the same data every time
2. **Start small**: Test with 100 assets before generating 10K+
3. **Validate early**: Run validation on small datasets first
4. **Monitor file size**: ~2-3KB per asset is normal
5. **Check relationships**: Ensure relationship count is reasonable (10-20% of assets)

---

## 🎉 You're Ready!

Generate your first payload now:

```bash
python3 aec_payload_generator.py
```

Happy generating! 🚀

