# AEC Payload Generator

A Python generator that creates realistic Autodesk/AutoCAD drawing payloads with configurable numbers of assets and relationships, following the exact structure of the AEC-Sample-Model-10K-Entities-Payload.json file.

## Features

- **10,000 Assets**: Generates realistic AEC assets across 8 categories
- **2,000 Relationships**: Creates meaningful relationships between assets
- **Realistic Distribution**: Matches real-world Revit model patterns
- **Proper Structure**: Follows Autodesk asset graph schema exactly
- **Configurable**: Customize asset counts, relationships, and output

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

This generates `aec_generated_payload.json` with:
- 10,000 assets
- 2,000 relationships
- ~20-30MB file size

### Custom Configuration

```bash
# Generate 5K assets and 1K relationships
python3 aec_payload_generator.py --assets 5000 --relationships 1000

# Specify output file
python3 aec_payload_generator.py --output my_model.json

# Use random seed for reproducibility
python3 aec_payload_generator.py --seed 42

# Combine options
python3 aec_payload_generator.py --assets 20000 --relationships 5000 --output large_model.json --seed 123
```

### Command Line Options

```
--assets N          Number of assets to generate (default: 10000)
--relationships N   Number of relationships to generate (default: 2000)
--output FILE       Output file path (default: aec_generated_payload.json)
--seed N           Random seed for reproducibility
```

## Output Structure

The generated JSON file follows this structure:

```json
{
  "batchId": "batch-aec-model-10000-entities",
  "description": "AEC Model with 10,000 entities - Generated payload",
  "modelStatistics": {
    "totalEntities": 10000,
    "modelSize": "25.3MB",
    "averageAssetSize": "2.5KB",
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
  "commands": [
    {
      "commandType": "CreateAssets",
      "batchNumber": 1,
      "assets": [ /* 10,000 assets */ ]
    }
  ],
  "relationships": [ /* 2,000 relationships */ ],
  "batchProcessingInfo": { /* ... */ },
  "generationInfo": { /* ... */ }
}
```

## Asset Structure Example

Each asset follows the Autodesk schema with:

- **id**: Unique identifier (e.g., `wall-000001`)
- **type**: Autodesk type ID (e.g., `autodesk.revit:wall-2.0.0`)
- **space**: Building space reference
- **attributes**: System attributes including uniqueId
- **components**: Metadata, properties, geometry, and custom properties

### Wall Example

```json
{
  "id": "wall-000001",
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

## Relationship Structure Example

```json
{
  "id": "rel-hosted-000001",
  "type": "autodesk.revit:hosted-1.0.0",
  "from": {"assetId": "door-000001"},
  "to": {"assetId": "wall-000001"},
  "attributes": {
    "application": {
      "relationshipType": "hosted",
      "insertionPoint": [10.5, 0, 0]
    }
  }
}
```

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

