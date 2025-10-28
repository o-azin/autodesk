# Data Schema Documentation

## Asset Document Schema

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `assetId` | String | Unique asset identifier (e.g., `tenant_revit_10k-asset-000001`) |
| `revisionId` | String | Unique revision identifier (e.g., `tenant_revit_10k-asset-000001-rev-1`) |
| `validFrom` | ISO8601 | Business time when asset became valid |
| `validTo` | Null | Business time when asset became invalid (null = current) |
| `transactionTime` | ISO8601 | System time when revision was recorded |
| `tenantId` | String | Tenant identifier (e.g., `tenant_revit_10k`) |
| `spaceId` | String | Space/level identifier (e.g., `space-level-1`) |
| `shardKey` | String | Shard key for distribution (format: `tenantId:spaceId`) |
| `type` | String | Asset type (e.g., `autodesk.revit:wall-2.0.0`) |
| `components` | Object | Asset components (metadata, geometry, properties) |

### Components Structure

```
components
├── insertions
    ├── metadata
    │   ├── typeId: "autodesk.revit:element-metadata-1.0.0"
    │   └── staticChildren
    │       ├── elementId: String
    │       ├── categoryId: String
    │       ├── phaseCreated: String
    │       └── phaseDemo: String
    ├── geometry
    │   ├── typeId: "autodesk.geometry:bounds-1.0.0"
    │   └── staticChildren
    │       ├── minPoint: Point3d [x, y, z]
    │       └── maxPoint: Point3d [x, y, z]
    └── properties
        ├── typeId: "autodesk.aec:component.propertyGroup-1.1.0"
        └── staticChildren
            └── properties
                ├── typeId: "map<autodesk.parameter:parameter-2.0.0>"
                └── insertions: { propertyName: propertyValue, ... }
```

### Property Value Structure

Each property in `insertions` has this structure:

```json
{
  "propertyName": {
    "typeId": "autodesk.revit.parameter:parameter-type-1.0.0",
    "staticChildren": {
      "value": {
        "typeId": "ValueType",
        "value": actualValue
      },
      "unit": {
        "typeId": "String",
        "value": "unitString"
      }
    }
  }
}
```

### Example Asset Document

```json
{
  "assetId": "tenant_revit_10k-asset-000001",
  "revisionId": "tenant_revit_10k-asset-000001-rev-1",
  "validFrom": "2025-10-28T10:00:00.000000",
  "validTo": null,
  "transactionTime": "2025-10-28T10:00:00.000000",
  "tenantId": "tenant_revit_10k",
  "spaceId": "space-level-1",
  "shardKey": "tenant_revit_10k:space-level-1",
  "type": "autodesk.revit:wall-2.0.0",
  "components": {
    "insertions": {
      "metadata": {
        "typeId": "autodesk.revit:element-metadata-1.0.0",
        "staticChildren": {
          "elementId": {
            "typeId": "String",
            "value": "1"
          },
          "categoryId": {
            "typeId": "String",
            "value": "OST_Walls"
          },
          "phaseCreated": {
            "typeId": "String",
            "value": "Existing"
          },
          "phaseDemo": {
            "typeId": "String",
            "value": "Phase 1"
          }
        }
      },
      "geometry": {
        "typeId": "autodesk.geometry:bounds-1.0.0",
        "staticChildren": {
          "minPoint": {
            "typeId": "Point3d",
            "value": [10.5, 20.3, 0]
          },
          "maxPoint": {
            "typeId": "Point3d",
            "value": [150.2, 200.5, 12.5]
          }
        }
      },
      "properties": {
        "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
        "staticChildren": {
          "properties": {
            "typeId": "map<autodesk.parameter:parameter-2.0.0>",
            "insertions": {
              "height": {
                "typeId": "autodesk.revit.parameter:height-1.0.0",
                "staticChildren": {
                  "value": {
                    "typeId": "Float64",
                    "value": 12.5
                  },
                  "unit": {
                    "typeId": "String",
                    "value": "ft"
                  }
                }
              },
              "mark": {
                "typeId": "autodesk.revit.parameter:mark-1.0.0",
                "staticChildren": {
                  "value": {
                    "typeId": "String",
                    "value": "M-1234"
                  }
                }
              },
              "material": {
                "typeId": "autodesk.revit.parameter:material-1.0.0",
                "staticChildren": {
                  "value": {
                    "typeId": "String",
                    "value": "Concrete"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Relationship Document Schema

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `relationshipId` | String | Unique relationship identifier |
| `fromAssetId` | String | Source asset ID |
| `toAssetId` | String | Target asset ID |
| `relationshipType` | String | Type of relationship |
| `validFrom` | ISO8601 | Business time when relationship became valid |
| `validTo` | Null | Business time when relationship became invalid (null = current) |
| `transactionTime` | ISO8601 | System time when relationship was recorded |
| `tenantId` | String | Tenant identifier |

### Relationship Types

| Type | Description |
|------|-------------|
| `hosted` | Asset is hosted in another asset |
| `roomBounding` | Asset bounds a room |
| `serves` | Asset serves another asset |
| `connects` | Asset connects to another asset |
| `contains` | Asset contains another asset |
| `supports` | Asset supports another asset |

### Example Relationship Document

```json
{
  "relationshipId": "tenant_revit_10k-asset-000001-hosted-tenant_revit_10k-asset-000002",
  "fromAssetId": "tenant_revit_10k-asset-000001",
  "toAssetId": "tenant_revit_10k-asset-000002",
  "relationshipType": "hosted",
  "validFrom": "2025-10-28T10:00:00.000000",
  "validTo": null,
  "transactionTime": "2025-10-28T10:00:00.000000",
  "tenantId": "tenant_revit_10k"
}
```

---

## Bitemporal Pattern

The schema implements a bitemporal pattern with two time dimensions:

### Business Time (validFrom, validTo)

- **validFrom**: When the asset state became valid in the business domain
- **validTo**: When the asset state became invalid (null = current state)
- Used for temporal queries: "What was the state at time T?"

### System Time (transactionTime)

- **transactionTime**: When the revision was recorded in the system
- Used for audit trails: "When was this change recorded?"

### Example: Asset Revision History

```
Asset: tenant_revit_10k-asset-000001

Revision 1 (rev-1):
  validFrom: 2025-01-01
  validTo: 2025-06-01
  transactionTime: 2025-01-01 10:00:00

Revision 2 (rev-2):
  validFrom: 2025-06-01
  validTo: null (current)
  transactionTime: 2025-06-01 14:30:00

Query: "What was the asset on 2025-03-15?"
Answer: Revision 1 (validFrom <= 2025-03-15 < validTo)
```

---

## Indexes

Recommended indexes for optimal query performance:

### Assets Collection

```javascript
// Direct ID lookup
db.assets.createIndex({ assetId: 1, validTo: 1 })

// Space queries
db.assets.createIndex({ spaceId: 1, validTo: 1 })

// Type queries
db.assets.createIndex({ type: 1, validTo: 1 })

// Compound queries
db.assets.createIndex({ assetId: 1, spaceId: 1, validTo: 1 })
db.assets.createIndex({ tenantId: 1, validTo: 1 })
```

### Relationships Collection

```javascript
// Outgoing relationships
db.relationships.createIndex({ fromAssetId: 1, validTo: 1 })

// Incoming relationships
db.relationships.createIndex({ toAssetId: 1, validTo: 1 })

// Type queries
db.relationships.createIndex({ relationshipType: 1, validTo: 1 })

// Tenant queries
db.relationships.createIndex({ tenantId: 1, validTo: 1 })
```

---

## Data Types

### Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `String` | Text value | `"M-1234"` |
| `Float64` | 64-bit floating point | `12.5` |
| `Int32` | 32-bit integer | `42` |
| `Boolean` | True/false | `true` |
| `Point3d` | 3D point | `[10.5, 20.3, 0]` |

### Revit Parameter Types

| Type | Description |
|------|-------------|
| `autodesk.revit.parameter:height-1.0.0` | Height parameter |
| `autodesk.revit.parameter:width-1.0.0` | Width parameter |
| `autodesk.revit.parameter:depth-1.0.0` | Depth parameter |
| `autodesk.revit.parameter:area-1.0.0` | Area parameter |
| `autodesk.revit.parameter:volume-1.0.0` | Volume parameter |
| `autodesk.revit.parameter:mark-1.0.0` | Mark/identifier |
| `autodesk.revit.parameter:comments-1.0.0` | Comments |
| `autodesk.revit.parameter:description-1.0.0` | Description |
| `autodesk.revit.parameter:fireRating-1.0.0` | Fire rating |
| `autodesk.revit.parameter:material-1.0.0` | Material |

---

## Statistics

### Generated Data

- **Total Assets**: 10,000
- **Total Relationships**: 30,000
- **Asset Types**: 8
- **Spaces**: 5
- **Relationship Types**: 6

### Property Distribution

- **P50**: 287 properties (50% of assets)
- **P75**: 592 properties (75% of assets)
- **P95**: 997 properties (95% of assets)
- **P99**: 4,491 properties (99% of assets)

### Asset Type Distribution

- Wall: 23%
- MEP Component: 20%
- Furniture: 23%
- Structural: 11.5%
- Room: 8.5%
- Window: 6%
- Door: 4%
- Fixture: 4%

