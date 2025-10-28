# Asset Graph Use Cases and AEC Model Analysis

## Executive Summary

This document provides a comprehensive analysis of Asset Graph workloads, access patterns, and detailed use-cases based on the Confluence page review and codebase analysis. It includes a P50 AEC model with near-realistic asset payloads for Revit-based workflows.

---

## Workload Overview

### Manufacturing (MFG) Workload
- **Tenants**: 2 Million+
- **Current Peak**: 5,261 entities/sec
- **Expected Peak (2026)**: 16,000 entities/sec with migration
- **Primary Pattern**: Snapshot-heavy, batch-friendly operations
- **Top Endpoints**: Relationship tracking (31.4M req/day), Asset closure (23.0M req/day)

### AEC Workload  
- **Tenants**: 2 Million+
- **Current Peak**: 3,000 entities/sec (Revit only)
- **Expected Peak (2026)**: 8,000 entities/sec (Revit) + 1,000 entities/sec (other clients)
- **Full Scale**: 30,000 entities/sec (full Revit) + 10,000 entities/sec (other clients)
- **Primary Pattern**: Write-heavy with burst patterns, batch operations

### AEC Revit Model Characteristics
| Percentile | Model Size (MB) | Asset Count | Avg Asset Size | Properties per Asset |
|------------|----------------|-------------|----------------|---------------------|
| **P50**    | 77 MB          | 35,000      | ~2.2 KB        | 100-300             |
| **P75**    | 179 MB         | 100,000     | ~1.8 KB        | 300-600             |
| **P95**    | 553 MB         | 400,000     | ~1.4 KB        | 600-1,000           |
| **P99**    | 1,190 MB       | 1,000,000   | ~1.2 KB        | 3,000-5,000         |

### Dynamic Properties Characteristics
- **PropertyGroup Component**: Contains dynamic properties ranging from 100 to 1,000 per asset (typical)
- **P99 Complex Assets**: Can contain 3,000-5,000 properties per asset
- **Property Types**: Revit parameters, custom parameters, calculated values, metadata
- **Common Categories**: Geometry, Material, Performance, Schedule, Identity, Constraints

---

## Access Patterns Analysis

### Core Entity Structure
Every entity in Asset Graph contains:
- **id**: Unique identifier
- **type**: Entity type with name and version
- **parent-id**: Hierarchical relationship (space → collection, asset → space)
- **attributes**: Key/value pairs for strongly consistent lookups
- **components**: JSON objects based on schema with properties
- **revisionId**: Version control
- **createdBy/lastModifiedBy**: Audit trail with dateTime, userId, clientId

### Primary Access Patterns

**Important Note**: All requests are collection-scoped, meaning every API call must include a collection identifier in the URL path.

#### 1. **Space Operations**

**Direct Space Retrieval**:
- Get specific space by ID: `GET /collections/{collectionId}/spaces/{spaceId}`

**Space Query Operations**:
- **Attribute-based filtering**: `attribute.{key} = {value}` (e.g., `attribute.buildingCode = "B001"`)
- **Type-based filtering**:
  - Exact version: `type.name=autodesk.space-type AND type.version=1.0.0`
  - Major version wildcard: `type.name=autodesk.space-type AND type.version=1.*.*`
  - Type name only: `type.name=autodesk.space-type`
- **Component-based filtering**:
  - Exact version: `component.type.name=autodesk.component-type AND type.version=1.0.0`
  - Major version wildcard: `component.type.name=autodesk.component-type AND type.version=1.*.*`
  - Type name only: `component.type.name=autodesk.component-type`

#### 2. **Asset Operations**

**Direct Asset Retrieval**:
- Get specific asset by ID within a space: `GET /collections/{collectionId}/spaces/{spaceId}/assets/{assetId}`

**Asset Query Operations**:
- **Attribute-based filtering**: `attribute.{key} = {value}` (e.g., `attribute.serialNumber = "SN-001"`)
- **Type-based filtering**:
  - Exact version: `type.name=autodesk.revit:wall AND type.version=2.0.0`
  - Major version wildcard: `type.name=autodesk.revit:wall AND type.version=2.*.*`
  - Type name only: `type.name=autodesk.revit:wall`
- **Component-based filtering**:
  - Exact version: `component.type.name=autodesk.geometry:bounds AND type.version=1.0.0`
  - Major version wildcard: `component.type.name=autodesk.geometry:bounds AND type.version=1.*.*`
  - Type name only: `component.type.name=autodesk.geometry:bounds`
- **Space scoping**: `space.id = {spaceId}` (filter assets within specific space)

#### 3. **Temporal Asset Queries**

**Time-based Asset Retrieval**:
- **Range with open end**: `from time = {timestamp} to latest` (within specified space)
- **Closed time range**: `from time = {startTime} to time = {endTime}`
- **Historical point-in-time**: `from start to time = {timestamp}`

#### 4. **Snapshot Operations**

**Direct Snapshot Retrieval**:
- Get specific snapshot by ID: `GET /collections/{collectionId}/snapshots/{snapshotId}`

**Snapshot Query Operations**:
- **Attribute-based filtering**: `attribute.{key} = {value}`
- **Type-based filtering**: Same patterns as spaces and assets
- **Component-based filtering**: Same patterns as spaces and assets
- **Space scoping**: `space.id = {spaceId}` (snapshots related to specific space)
- **Asset inclusion filtering**: 
  - Single asset: `contains asset.id = {assetId}`
  - Multiple assets: `contains asset.id = {assetId1} OR asset.id = {assetId2}`

#### 5. **Relationship Operations**

**Direct Relationship Retrieval**:
- Get specific relationship by ID: `GET /collections/{collectionId}/relationships/{relationshipId}`

**Relationship Traversal**:
- **Outgoing relationships**: Find assets where `asset.id = {sourceId}` is the "from" asset
- **Incoming relationships**: Find assets where `asset.id = {targetId}` is the "to" asset
- **Multi-depth traversal**: Navigate relationship chains with configurable depth limits
- **Advanced filtering**:
  - Source asset type: `from.asset.type = {assetType}`
  - Target asset type: `to.asset.type = {assetType}`
  - Relationship type: `relationship.type = {relationshipType}`
  - Component filtering: `relationship.component.type = {componentType}`
  - Temporal filtering: `revision.createdTime >= {timestamp}`

#### 6. **Reference-Based Queries** (Alternative to Relationships)

**Space-to-Space References**:
- Find spaces referencing a specific space: `component.reference.space.id = {spaceId}`

**Asset-to-Asset References**:
- Find assets referencing a specific asset: `component.reference.asset.id = {assetId}`

#### 7. **Component Property Search**

**Dynamic Property Filtering**:
- **Single property**: `component.property.{key1} = {value1}`
- **Multiple properties with AND**: `component.property.{key1} = {value1} AND component.property.{key2} > {value2}`
- **Multiple properties with OR**: `component.property.{key1} = {value1} OR component.property.{key2} < {value2}`
- **Complex combinations**: Support for nested AND/OR logic across multiple component properties

#### 8. **Bulk Operations**

**Bulk Asset Download**:
- **Space-scoped bulk download**: Download all assets within a space (100K to 1M assets)
- **Filtered bulk download**: Apply query filters to bulk operations
- **Streaming download**: Large result sets delivered via streaming responses
- **Batch processing**: Results delivered in configurable batch sizes for memory efficiency

### Query Pattern Statistics (68.2% of 13.1M queries)
- **Direct ID lookups**: 8.95M queries (single entity retrieval)
- **Filtered queries**: 3.16M queries (attribute/component-based)
- **Temporal queries**: 681K queries (time-based retrieval)
- **Relationship traversal**: 323K queries (graph operations)

---

## Detailed Use Cases

### Use Case 1: AEC Revit Model Import (High Volume)
**Scenario**: Architect uploads a P50 Revit model (77MB, 35,000 assets)

**Access Pattern Flow**:
```
1. Batch Creation: POST /v2/collections/{id}/batches
2. Bulk Asset Addition: PUT /v2/collections/{id}/batches/{batchId}:add (905.4K req/day)
3. Batch Processing: GET /beta/v2/collections/{id}/ordered-batches/{batchId} (259.8K req/day)
4. Asset Queries: GET /v1/collections/{id}/assets (184.7K req/day)
```

**Payload Characteristics**:
- **Batch Size**: 25 commands max (stateless batch)
- **Command Size**: 250KB max per command
- **Total Payload**: 250KB max per batch
- **Asset Distribution**: 1,400 batches of 25 assets each

**Real-time Example**:
```json
{
  "commands": [
    {
      "commandType": "CreateAssets",
      "assets": [
        {
          "id": "wall-001-level-1",
          "type": "autodesk.revit:wall-2.0.0",
          "space": {"id": "space-building-model"},
          "attributes": {
            "application": {
              "familyName": "Basic Wall",
              "typeName": "Generic - 8\"",
              "level": "Level 1",
              "roomBounding": true
            },
            "system": {
              "elementId": "316789",
              "uniqueId": "e7d0c1a2-3b4c-5d6e-7f8g-9h0i1j2k3l4m"
            }
          },
          "components": {
            "insertions": {
              "geometry": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [10, 0.67, 3]}
                }
              },
              "properties": {
                "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                "staticChildren": {
                  "properties": {
                    "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                    "insertions": {
                      "area": {
                        "typeId": "autodesk.revit.parameter:area-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 30.0},
                          "unit": {"typeId": "String", "value": "sqft"}
                        }
                      },
                      "volume": {
                        "typeId": "autodesk.revit.parameter:volume-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 20.1},
                          "unit": {"typeId": "String", "value": "cuft"}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      ]
    }
  ]
}
```

### Use Case 2: Manufacturing Equipment Tracking (Relationship Heavy)
**Scenario**: Track manufacturing equipment relationships and dependencies

**Access Pattern Flow**:
```
1. Equipment Asset Lookup: GET /collections/{id}/assets/{equipmentId}
2. Relationship Traversal: GET /collections/{id}/assets/{id}/relationships/revisions (31.4M req/day)
3. Closure Operations: GET /collections/{id}/assets/{id}/closure (23.0M req/day)
4. Revision History: GET /collections/{id}/assets/{id}/revisions (8.7M req/day)
```

**Real-time Example**:
```json
{
  "assets": [
    {
      "id": "cnc-machine-floor-a-001",
      "type": "autodesk.manufacturing:equipment-1.0.0",
      "space": {"id": "space-factory-floor-a"},
      "attributes": {
        "application": {
          "serialNumber": "MFG-2024-001",
          "equipmentType": "CNC_MACHINE",
          "manufacturer": "ACME Industries",
          "installationDate": "2024-01-15",
          "operationalStatus": "operational"
        },
        "system": {
          "maintenanceWindow": "2024-01-20T02:00:00Z",
          "lastInspection": "2024-01-10T14:30:00Z"
        }
      },
      "components": {
        "insertions": {
          "specifications": {
            "typeId": "autodesk.manufacturing:cnc-specs-1.0.0",
            "staticChildren": {
              "maxSpindleSpeed": {"typeId": "Int32", "value": 12000},
              "toolCapacity": {"typeId": "Int32", "value": 24},
              "workEnvelope": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [2.5, 1.8, 2.2]}
                }
              }
            }
          }
        }
      }
    }
  ],
  "relationships": [
    {
      "id": "rel-cnc-to-controller",
      "type": "autodesk.manufacturing:controls-1.0.0",
      "from": {"assetId": "cnc-machine-floor-a-001"},
      "to": {"assetId": "plc-controller-001"},
      "attributes": {
        "application": {
          "connectionType": "ethernet",
          "protocol": "modbus-tcp"
        }
      }
    }
  ]
}
```

### Use Case 3: Temporal State Queries (Historical Analysis)
**Scenario**: Retrieve building state at specific time for compliance audit

**Access Pattern Flow**:
```
1. Time-based Query: GET /collections/{id}/assets?from=2024-01-01&to=2024-01-31
2. Snapshot Retrieval: GET /v2/collections/{id}/snapshots (15.8M req/day)
3. Asset State Reconstruction: Multiple asset queries with temporal filters
```

**Real-time Example**:
```json
{
  "query": {
    "timeRange": {
      "from": "2024-01-01T00:00:00Z",
      "to": "2024-01-31T23:59:59Z"
    },
    "filters": {
      "and": [
        {"attribute.application.buildingCode": "B001"},
        {"type.name": "autodesk.revit:room"},
        {"component.type.name": "autodesk.aec:occupancy"}
      ]
    }
  }
}
```

### Use Case 4: Component Property Filtering (Search Heavy)
**Scenario**: Find all HVAC equipment with specific efficiency ratings

**Access Pattern Flow**:
```
1. Component Search: component.property.efficiency>0.85
2. Type Filtering: type.name=autodesk.mep:hvac-equipment
3. Attribute Filtering: attribute.application.status=active
```

**Real-time Example**:
```json
{
  "query": {
    "filters": {
      "and": [
        {
          "component": {
            "type": "autodesk.mep:hvac-equipment-1.0.0",
            "property": {
              "path": "specifications.efficiency",
              "operator": ">=",
              "value": 0.85
            }
          }
        },
        {
          "attribute": {
            "path": "application.status",
            "operator": "=",
            "value": "active"
          }
        }
      ]
    }
  }
}
```

### Use Case 5: Dynamic Property Querying (High-Volume Property Search)
**Scenario**: Query assets across space or collection based on dynamic Revit parameters

**Access Pattern Flow**:
```
1. Property Search: component.propertyGroup.properties.{dynamicKey}=value
2. Space/Collection Scoping: space.id=123 OR collection.id=456
3. Multi-Property Filtering: AND/OR combinations across 100-5,000 properties
4. Aggregation Queries: COUNT, SUM, AVG across property values
```

**Property Volume Characteristics**:
- **Typical Assets**: 100-300 properties per asset
- **Complex Assets**: 600-1,000 properties per asset  
- **P99 Complex Assets**: 3,000-5,000 properties per asset
- **Total Properties per Space**: 35,000 assets × 300 avg properties = 10.5M properties
- **P99 Space**: 1M assets × 3,000 properties = 3B properties

**Real-time Example**:
```json
{
  "query": {
    "scope": {
      "type": "space",
      "id": "space-building-level-1"
    },
    "filters": {
      "and": [
        {
          "component": {
            "type": "autodesk.aec:component.propertyGroup-1.1.0",
            "property": {
              "path": "properties.thermalTransmittance.value",
              "operator": "<=",
              "value": 0.5
            }
          }
        },
        {
          "component": {
            "type": "autodesk.aec:component.propertyGroup-1.1.0",
            "property": {
              "path": "properties.fireRating.value",
              "operator": ">=",
              "value": "1HR"
            }
          }
        },
        {
          "component": {
            "type": "autodesk.aec:component.propertyGroup-1.1.0",
            "property": {
              "path": "properties.structuralUsage.value",
              "operator": "=",
              "value": "Bearing"
            }
          }
        }
      ]
    },
    "aggregations": {
      "totalArea": {
        "sum": "properties.area.value"
      },
      "averageHeight": {
        "avg": "properties.height.value"
      },
      "countByMaterial": {
        "terms": "properties.material.value"
      }
    }
  }
}
```


## P50 AEC Model with Asset Payload

### Model Characteristics (P50 - 77MB, 35,000 assets)
- **Average Asset Size**: 2.2KB
- **Typical Distribution**:
  - Walls: 8,000 assets (23%)
  - Doors/Windows: 5,000 assets (14%)
  - Rooms/Spaces: 3,000 assets (9%)
  - MEP Components: 7,000 assets (20%)
  - Structural Elements: 4,000 assets (11%)
  - Furniture/Fixtures: 8,000 assets (23%)

### Complete P50 AEC Asset Payload Example

```json
{
  "batchId": "batch-revit-model-p50-001",
  "commands": [
    {
      "commandType": "CreateAssets",
      "assets": [
        {
          "id": "wall-exterior-north-001",
          "type": "autodesk.revit:wall-2.0.0",
          "space": {"id": "space-building-level-1"},
          "attributes": {
            "system": {
              "uniqueId": "e7d0c1a2-3b4c-5d6e-7f8g-9h0i1j2k3l4m"
            }
          },
          "components": {
            "insertions": {
              "metadata": {
                "typeId": "autodesk.revit:element-metadata-1.0.0",
                "staticChildren": {
                  "elementId": {"typeId": "String", "value": "316789"},
                  "categoryId": {"typeId": "String", "value": "OST_Walls"},
                  "phaseCreated": {"typeId": "String", "value": "New Construction"},
                  "phaseDemo": {"typeId": "String", "value": "None"}
                }
              },
              "wallProperties": {
                "typeId": "autodesk.revit:wall-properties-1.0.0",
                "staticChildren": {
                  "familyName": {"typeId": "String", "value": "Exterior Wall"},
                  "typeName": {"typeId": "String", "value": "Brick on CMU"},
                  "level": {"typeId": "String", "value": "Level 1"},
                  "roomBounding": {"typeId": "Bool", "value": true},
                  "fireRating": {"typeId": "String", "value": "2HR"}
                }
              },
              "thermalProperties": {
                "typeId": "autodesk.revit:thermal-properties-1.0.0",
                "staticChildren": {
                  "rValue": {"typeId": "Float64", "value": 15.2},
                  "uValue": {"typeId": "Float64", "value": 0.066}
                }
              },
              "geometry": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [20, 0.75, 12]},
                  "centerPoint": {"typeId": "Point3d", "value": [10, 0.375, 6]}
                }
              },
              "material": {
                "typeId": "autodesk.revit:material-1.0.0",
                "staticChildren": {
                  "layers": {
                    "typeId": "Array<autodesk.revit:materialLayer-1.0.0>",
                    "value": [
                      {
                        "materialId": "brick-common",
                        "thickness": 0.33,
                        "function": "finish"
                      },
                      {
                        "materialId": "cmu-8inch",
                        "thickness": 0.67,
                        "function": "structure"
                      }
                    ]
                  }
                }
              },
              "properties": {
                "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                "staticChildren": {
                  "properties": {
                    "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                    "insertions": {
                      "area": {
                        "typeId": "autodesk.revit.parameter:area-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 240.0},
                          "unit": {"typeId": "String", "value": "sqft"}
                        }
                      },
                      "volume": {
                        "typeId": "autodesk.revit.parameter:volume-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 180.0},
                          "unit": {"typeId": "String", "value": "cuft"}
                        }
                      },
                      "length": {
                        "typeId": "autodesk.revit.parameter:length-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 20.0},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      },
                      "height": {
                        "typeId": "autodesk.revit.parameter:height-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 12.0},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      }
                    }
                  }
                }
              },
              "schedule": {
                "typeId": "autodesk.revit:schedule-1.0.0",
                "staticChildren": {
                  "scheduleId": {"typeId": "String", "value": "Wall Schedule"},
                  "mark": {"typeId": "String", "value": "W-1"},
                  "comments": {"typeId": "String", "value": "Load bearing exterior wall"}
                }
              }
            }
          }
        },
        {
          "id": "door-entry-main-001",
          "type": "autodesk.revit:door-2.0.0",
          "space": {"id": "space-building-level-1"},
          "attributes": {
            "system": {
              "uniqueId": "f8e1d2b3-4c5d-6e7f-8g9h-0i1j2k3l4m5n"
            }
          },
          "components": {
            "insertions": {
              "metadata": {
                "typeId": "autodesk.revit:element-metadata-1.0.0",
                "staticChildren": {
                  "elementId": {"typeId": "String", "value": "318456"},
                  "categoryId": {"typeId": "String", "value": "OST_Doors"},
                  "hostElementId": {"typeId": "String", "value": "316789"}
                }
              },
              "doorProperties": {
                "typeId": "autodesk.revit:door-properties-1.0.0",
                "staticChildren": {
                  "familyName": {"typeId": "String", "value": "Single-Flush"},
                  "typeName": {"typeId": "String", "value": "36\" x 84\""},
                  "level": {"typeId": "String", "value": "Level 1"},
                  "roomBounding": {"typeId": "Bool", "value": false},
                  "fireRating": {"typeId": "String", "value": "20MIN"},
                  "securityLevel": {"typeId": "String", "value": "Standard"}
                }
              },
              "geometry": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [3, 0.17, 7]},
                  "insertionPoint": {"typeId": "Point3d", "value": [10, 0, 0]}
                }
              },
              "hardware": {
                "typeId": "autodesk.revit:doorHardware-1.0.0",
                "staticChildren": {
                  "lockset": {"typeId": "String", "value": "Schlage B560"},
                  "hinges": {"typeId": "String", "value": "Ives 5BB1"},
                  "closer": {"typeId": "String", "value": "LCN 4040XP"}
                }
              },
              "properties": {
                "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                "staticChildren": {
                  "properties": {
                    "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                    "insertions": {
                      "width": {
                        "typeId": "autodesk.revit.parameter:width-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 3.0},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      },
                      "height": {
                        "typeId": "autodesk.revit.parameter:height-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 7.0},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      },
                      "thickness": {
                        "typeId": "autodesk.revit.parameter:thickness-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 0.17},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        {
          "id": "room-office-101",
          "type": "autodesk.revit:room-2.0.0",
          "space": {"id": "space-building-level-1"},
          "attributes": {
            "system": {
              "uniqueId": "g9f2e3d4-5c6d-7e8f-9g0h-1i2j3k4l5m6n"
            }
          },
          "components": {
            "insertions": {
              "metadata": {
                "typeId": "autodesk.revit:element-metadata-1.0.0",
                "staticChildren": {
                  "elementId": {"typeId": "String", "value": "320123"},
                  "categoryId": {"typeId": "String", "value": "OST_Rooms"},
                  "level": {"typeId": "String", "value": "Level 1"}
                }
              },
              "roomProperties": {
                "typeId": "autodesk.revit:room-properties-1.0.0",
                "staticChildren": {
                  "name": {"typeId": "String", "value": "Office 101"},
                  "number": {"typeId": "String", "value": "101"},
                  "department": {"typeId": "String", "value": "Administration"},
                  "occupancyType": {"typeId": "String", "value": "Office"},
                  "occupantLoad": {"typeId": "Int32", "value": 4}
                }
              },
              "geometry": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [12, 10, 9]},
                  "centerPoint": {"typeId": "Point3d", "value": [6, 5, 4.5]}
                }
              },
              "occupancy": {
                "typeId": "autodesk.aec:occupancy-1.0.0",
                "staticChildren": {
                  "occupancyClassification": {"typeId": "String", "value": "Business"},
                  "maxOccupants": {"typeId": "Int32", "value": 4},
                  "accessibilityCompliant": {"typeId": "Bool", "value": true}
                }
              },
              "properties": {
                "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                "staticChildren": {
                  "properties": {
                    "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                    "insertions": {
                      "area": {
                        "typeId": "autodesk.revit.parameter:area-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 120.0},
                          "unit": {"typeId": "String", "value": "sqft"}
                        }
                      },
                      "volume": {
                        "typeId": "autodesk.revit.parameter:volume-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 1080.0},
                          "unit": {"typeId": "String", "value": "cuft"}
                        }
                      },
                      "perimeter": {
                        "typeId": "autodesk.revit.parameter:perimeter-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 44.0},
                          "unit": {"typeId": "String", "value": "ft"}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        },
        {
          "id": "hvac-vav-101",
          "type": "autodesk.mep:hvac-terminal-1.0.0",
          "space": {"id": "space-building-level-1"},
          "attributes": {
            "system": {
              "uniqueId": "h0g3f4e5-6d7e-8f9g-0h1i-2j3k4l5m6n7o"
            }
          },
          "components": {
            "insertions": {
              "metadata": {
                "typeId": "autodesk.revit:element-metadata-1.0.0",
                "staticChildren": {
                  "elementId": {"typeId": "String", "value": "325789"},
                  "categoryId": {"typeId": "String", "value": "OST_DuctTerminal"},
                  "mechanicalSystem": {"typeId": "String", "value": "HVAC-1"}
                }
              },
              "hvacProperties": {
                "typeId": "autodesk.mep:hvac-properties-1.0.0",
                "staticChildren": {
                  "familyName": {"typeId": "String", "value": "VAV Terminal"},
                  "typeName": {"typeId": "String", "value": "VAV w/ Reheat - 500 CFM"},
                  "systemName": {"typeId": "String", "value": "Supply Air System 1"},
                  "servedSpace": {"typeId": "String", "value": "Office 101"},
                  "controlSequence": {"typeId": "String", "value": "VAV with Reheat"}
                }
              },
              "geometry": {
                "typeId": "autodesk.geometry:bounds-1.0.0",
                "staticChildren": {
                  "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                  "maxPoint": {"typeId": "Point3d", "value": [2, 1.5, 1]},
                  "insertionPoint": {"typeId": "Point3d", "value": [6, 5, 8.5]}
                }
              },
              "performance": {
                "typeId": "autodesk.mep:hvac-performance-1.0.0",
                "staticChildren": {
                  "maxAirflow": {"typeId": "Float64", "value": 500.0},
                  "minAirflow": {"typeId": "Float64", "value": 100.0},
                  "heatingCapacity": {"typeId": "Float64", "value": 2000.0},
                  "pressureDrop": {"typeId": "Float64", "value": 0.25}
                }
              },
              "properties": {
                "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                "staticChildren": {
                  "properties": {
                    "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                    "insertions": {
                      "airflow": {
                        "typeId": "autodesk.mep.parameter:airflow-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 350.0},
                          "unit": {"typeId": "String", "value": "CFM"}
                        }
                      },
                      "staticPressure": {
                        "typeId": "autodesk.mep.parameter:pressure-1.0.0",
                        "staticChildren": {
                          "value": {"typeId": "Float64", "value": 0.75},
                          "unit": {"typeId": "String", "value": "in. w.g."}
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      ]
    }
  ],
  "relationships": [
    {
      "id": "rel-door-in-wall",
      "type": "autodesk.revit:hosted-1.0.0",
      "from": {"assetId": "door-entry-main-001"},
      "to": {"assetId": "wall-exterior-north-001"},
      "attributes": {
        "application": {
          "relationshipType": "hosted",
          "insertionPoint": [10, 0, 0]
        }
      }
    },
    {
      "id": "rel-room-bounded-by-wall",
      "type": "autodesk.revit:roomBounding-1.0.0",
      "from": {"assetId": "room-office-101"},
      "to": {"assetId": "wall-exterior-north-001"},
      "attributes": {
        "application": {
          "relationshipType": "roomBounding",
          "boundaryType": "exterior"
        }
      }
    },
    {
      "id": "rel-hvac-serves-room",
      "type": "autodesk.mep:serves-1.0.0",
      "from": {"assetId": "hvac-vav-101"},
      "to": {"assetId": "room-office-101"},
      "attributes": {
        "application": {
          "relationshipType": "serves",
          "serviceType": "ventilation"
        }
      }
    }
  ]
}
```

