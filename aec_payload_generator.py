#!/usr/bin/env python3
"""
AEC Payload Generator
Generates realistic Autodesk/AutoCAD drawing payloads with individual documents for MongoDB.
Each asset and relationship is stored as a separate document with a reference to the parent model.

Use like this:
python3 aec_payload_generator.py --assets 5000 --relationships 1000 --output-dir output_folder
"""

import json
import random
import uuid
import os
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path


class AECPayloadGenerator:
    """Generator for AEC model payloads with realistic asset distribution."""
    
    # Asset type configurations
    ASSET_TYPES = {
        'walls': {
            'count': 2300,
            'type': 'autodesk.revit:wall-2.0.0',
            'category': 'OST_Walls',
            'element_id_start': 316000,
            'families': [
                ('Exterior Wall', ['Brick on CMU', 'Concrete - 12"', 'Metal Panel']),
                ('Interior Wall', ['Generic - 6"', 'Generic - 4"', 'Gypsum - 5"'])
            ]
        },
        'doors': {
            'count': 400,
            'type': 'autodesk.revit:door-2.0.0',
            'category': 'OST_Doors',
            'element_id_start': 318000,
            'families': [
                ('Single-Flush', ['36" x 84"', '32" x 80"', '30" x 80"']),
                ('Double-Flush', ['72" x 84"', '60" x 84"'])
            ],
            'hosted': True
        },
        'windows': {
            'count': 600,
            'type': 'autodesk.revit:window-2.0.0',
            'category': 'OST_Windows',
            'element_id_start': 319000,
            'families': [
                ('Fixed', ['48" x 72"', '36" x 60"', '24" x 48"']),
                ('Casement', ['36" x 48"', '24" x 36"'])
            ],
            'hosted': True
        },
        'rooms': {
            'count': 850,
            'type': 'autodesk.revit:room-2.0.0',
            'category': 'OST_Rooms',
            'element_id_start': 320000,
            'departments': ['Administration', 'Engineering', 'Sales', 'Operations', 'IT'],
            'occupancy_types': ['Office', 'Conference', 'Storage', 'Lobby', 'Break Room']
        },
        'mepComponents': {
            'count': 2000,
            'type': 'autodesk.mep:hvac-terminal-1.0.0',
            'category': 'OST_DuctTerminal',
            'element_id_start': 325000,
            'families': [
                ('VAV Terminal', ['VAV w/ Reheat - 350 CFM', 'VAV w/ Reheat - 500 CFM']),
                ('Diffuser', ['4-Way - 24x24', '2-Way - 24x12'])
            ]
        },
        'structuralElements': {
            'count': 1150,
            'type': 'autodesk.revit:structural-framing-2.0.0',
            'category': 'OST_StructuralFraming',
            'element_id_start': 330000,
            'families': [
                ('W-Wide Flange', ['W12X26', 'W14X30', 'W16X40']),
                ('HSS-Hollow Structural Section', ['HSS8X8X1/2', 'HSS6X6X3/8'])
            ]
        },
        'furniture': {
            'count': 2300,
            'type': 'autodesk.revit:furniture-2.0.0',
            'category': 'OST_Furniture',
            'element_id_start': 340000,
            'families': [
                ('Desk', ['60" x 30"', '72" x 36"', '48" x 24"']),
                ('Chair', ['Task Chair', 'Executive Chair', 'Guest Chair']),
                ('Table', ['Conference - 96" x 48"', 'Break Room - 48" x 30"'])
            ]
        },
        'fixtures': {
            'count': 400,
            'type': 'autodesk.revit:lighting-fixture-2.0.0',
            'category': 'OST_LightingFixtures',
            'element_id_start': 350000,
            'families': [
                ('Troffer Light', ['2x4 LED - 40W', '2x2 LED - 28W']),
                ('Pendant', ['LED - 15W', 'LED - 25W'])
            ]
        }
    }
    
    LEVELS = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
    PHASES = ['New Construction', 'Existing', 'Demolition', 'Future']
    
    def __init__(self, total_assets: int = 10000, total_relationships: int = 2000, model_id: str = None):
        self.total_assets = total_assets
        self.total_relationships = total_relationships
        self.generated_assets = []
        self.asset_ids_by_type = {key: [] for key in self.ASSET_TYPES.keys()}
        self.model_id = model_id or f"model-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    def generate_uuid(self, prefix: str, index: int) -> str:
        """Generate a deterministic UUID-like string."""
        base = f"{prefix}-{index:04d}"
        # Create a UUID-like format
        parts = [
            f"{random.randint(0, 0xffffffff):08x}",
            f"{random.randint(0, 0xffff):04x}",
            f"{random.randint(0, 0xffff):04x}",
            f"{random.randint(0, 0xffff):04x}",
            f"{random.randint(0, 0xffffffffffff):012x}"
        ]
        return '-'.join(parts) + f"-{index:03d}"
    
    def generate_point3d(self, x_range=(0, 100), y_range=(0, 100), z_range=(0, 15)) -> List[float]:
        """Generate a random 3D point."""
        return [
            round(random.uniform(*x_range), 2),
            round(random.uniform(*y_range), 2),
            round(random.uniform(*z_range), 2)
        ]
    
    def generate_wall(self, index: int, config: Dict) -> Dict:
        """Generate a wall asset."""
        asset_id = f"wall-{index:06d}"
        family, types = random.choice(config['families'])
        type_name = random.choice(types)
        level = random.choice(self.LEVELS)

        # Generate geometry
        x_start = random.uniform(0, 90)
        y_start = random.uniform(0, 90)
        length = random.uniform(10, 30)
        height = random.uniform(9, 14)
        thickness = 0.5 if 'Interior' in family else 0.75

        area = length * height
        volume = area * thickness

        asset = {
            "modelId": self.model_id,
            "id": asset_id,
            "type": config['type'],
            "space": {"id": f"space-building-{level.lower().replace(' ', '-')}"},
            "attributes": {
                "system": {
                    "uniqueId": self.generate_uuid("wall", index)
                }
            },
            "components": {
                "insertions": {
                    "metadata": {
                        "typeId": "autodesk.revit:element-metadata-1.0.0",
                        "staticChildren": {
                            "elementId": {"typeId": "String", "value": str(config['element_id_start'] + index)},
                            "categoryId": {"typeId": "String", "value": config['category']},
                            "phaseCreated": {"typeId": "String", "value": random.choice(self.PHASES)}
                        }
                    },
                    "wallProperties": {
                        "typeId": "autodesk.revit:wall-properties-1.0.0",
                        "staticChildren": {
                            "familyName": {"typeId": "String", "value": family},
                            "typeName": {"typeId": "String", "value": type_name},
                            "level": {"typeId": "String", "value": level},
                            "roomBounding": {"typeId": "Bool", "value": random.choice([True, False])}
                        }
                    },
                    "geometry": {
                        "typeId": "autodesk.geometry:bounds-1.0.0",
                        "staticChildren": {
                            "minPoint": {"typeId": "Point3d", "value": [x_start, y_start, 0]},
                            "maxPoint": {"typeId": "Point3d", "value": [x_start + length, y_start + thickness, height]}
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
                                            "value": {"typeId": "Float64", "value": round(area, 2)},
                                            "unit": {"typeId": "String", "value": "sqft"}
                                        }
                                    },
                                    "volume": {
                                        "typeId": "autodesk.revit.parameter:volume-1.0.0",
                                        "staticChildren": {
                                            "value": {"typeId": "Float64", "value": round(volume, 2)},
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
        
        return asset
    
    def generate_door(self, index: int, config: Dict) -> Dict:
        """Generate a door asset."""
        asset_id = f"door-{index:06d}"
        family, types = random.choice(config['families'])
        type_name = random.choice(types)
        level = random.choice(self.LEVELS)

        # Parse dimensions from type name
        width = float(type_name.split('"')[0]) / 12  # Convert inches to feet
        height = 7.0

        asset = {
            "modelId": self.model_id,
            "id": asset_id,
            "type": config['type'],
            "space": {"id": f"space-building-{level.lower().replace(' ', '-')}"},
            "attributes": {
                "system": {
                    "uniqueId": self.generate_uuid("door", index)
                }
            },
            "components": {
                "insertions": {
                    "metadata": {
                        "typeId": "autodesk.revit:element-metadata-1.0.0",
                        "staticChildren": {
                            "elementId": {"typeId": "String", "value": str(config['element_id_start'] + index)},
                            "categoryId": {"typeId": "String", "value": config['category']}
                        }
                    },
                    "doorProperties": {
                        "typeId": "autodesk.revit:door-properties-1.0.0",
                        "staticChildren": {
                            "familyName": {"typeId": "String", "value": family},
                            "typeName": {"typeId": "String", "value": type_name},
                            "level": {"typeId": "String", "value": level},
                            "roomBounding": {"typeId": "Bool", "value": False}
                        }
                    },
                    "geometry": {
                        "typeId": "autodesk.geometry:bounds-1.0.0",
                        "staticChildren": {
                            "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                            "maxPoint": {"typeId": "Point3d", "value": [width, 0.17, height]},
                            "insertionPoint": {"typeId": "Point3d", "value": self.generate_point3d()}
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
                                            "value": {"typeId": "Float64", "value": round(width, 2)},
                                            "unit": {"typeId": "String", "value": "ft"}
                                        }
                                    },
                                    "height": {
                                        "typeId": "autodesk.revit.parameter:height-1.0.0",
                                        "staticChildren": {
                                            "value": {"typeId": "Float64", "value": height},
                                            "unit": {"typeId": "String", "value": "ft"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return asset

    def generate_window(self, index: int, config: Dict) -> Dict:
        """Generate a window asset."""
        asset_id = f"window-{index:06d}"
        family, types = random.choice(config['families'])
        type_name = random.choice(types)
        level = random.choice(self.LEVELS)

        # Parse dimensions
        width = float(type_name.split('"')[0]) / 12
        height = 6.0

        asset = {
            "modelId": self.model_id,
            "id": asset_id,
            "type": config['type'],
            "space": {"id": f"space-building-{level.lower().replace(' ', '-')}"},
            "attributes": {
                "system": {
                    "uniqueId": self.generate_uuid("window", index)
                }
            },
            "components": {
                "insertions": {
                    "metadata": {
                        "typeId": "autodesk.revit:element-metadata-1.0.0",
                        "staticChildren": {
                            "elementId": {"typeId": "String", "value": str(config['element_id_start'] + index)},
                            "categoryId": {"typeId": "String", "value": config['category']}
                        }
                    },
                    "windowProperties": {
                        "typeId": "autodesk.revit:window-properties-1.0.0",
                        "staticChildren": {
                            "familyName": {"typeId": "String", "value": family},
                            "typeName": {"typeId": "String", "value": type_name},
                            "level": {"typeId": "String", "value": level},
                            "roomBounding": {"typeId": "Bool", "value": False}
                        }
                    },
                    "geometry": {
                        "typeId": "autodesk.geometry:bounds-1.0.0",
                        "staticChildren": {
                            "minPoint": {"typeId": "Point3d", "value": [0, 0, 0]},
                            "maxPoint": {"typeId": "Point3d", "value": [width, 0.17, height]},
                            "insertionPoint": {"typeId": "Point3d", "value": self.generate_point3d()}
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
                                            "value": {"typeId": "Float64", "value": round(width, 2)},
                                            "unit": {"typeId": "String", "value": "ft"}
                                        }
                                    },
                                    "height": {
                                        "typeId": "autodesk.revit.parameter:height-1.0.0",
                                        "staticChildren": {
                                            "value": {"typeId": "Float64", "value": height},
                                            "unit": {"typeId": "String", "value": "ft"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        return asset

    def generate_room(self, index: int, config: Dict) -> Dict:
        """Generate a room asset."""
        asset_id = f"room-{index:06d}"
        level = random.choice(self.LEVELS)
        department = random.choice(config['departments'])
        occupancy_type = random.choice(config['occupancy_types'])

        # Generate room dimensions
        width = random.uniform(10, 20)
        depth = random.uniform(10, 20)
        height = random.uniform(9, 12)
        area = width * depth
        volume = area * height

        asset = {
            "modelId": self.model_id,
            "id": asset_id,
            "type": config['type'],
            "space": {"id": f"space-building-{level.lower().replace(' ', '-')}"},
            "attributes": {
                "system": {
                    "uniqueId": self.generate_uuid("room", index)
                }
            },
            "components": {
                "insertions": {
                    "metadata": {
                        "typeId": "autodesk.revit:element-metadata-1.0.0",
                        "staticChildren": {
                            "elementId": {"typeId": "String", "value": str(config['element_id_start'] + index)},
                            "categoryId": {"typeId": "String", "value": config['category']},
                            "level": {"typeId": "String", "value": level}
                        }
                    },
                    "roomProperties": {
                        "typeId": "autodesk.revit:room-properties-1.0.0",
                        "staticChildren": {
                            "name": {"typeId": "String", "value": f"{occupancy_type} {100 + index}"},
                            "number": {"typeId": "String", "value": str(100 + index)},
                            "department": {"typeId": "String", "value": department},
                            "occupancyType": {"typeId": "String", "value": occupancy_type},
                            "occupantLoad": {"typeId": "Int32", "value": random.randint(1, 10)}
                        }
                    },
                    "geometry": {
                        "typeId": "autodesk.geometry:bounds-1.0.0",
                        "staticChildren": {
                            "minPoint": {"typeId": "Point3d", "value": self.generate_point3d()},
                            "maxPoint": {"typeId": "Point3d", "value": [width, depth, height]}
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
                                            "value": {"typeId": "Float64", "value": round(area, 2)},
                                            "unit": {"typeId": "String", "value": "sqft"}
                                        }
                                    },
                                    "volume": {
                                        "typeId": "autodesk.revit.parameter:volume-1.0.0",
                                        "staticChildren": {
                                            "value": {"typeId": "Float64", "value": round(volume, 2)},
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

        return asset

    def generate_generic_asset(self, asset_type: str, index: int, config: Dict) -> Dict:
        """Generate a generic asset for MEP, structural, furniture, and fixtures."""
        asset_id = f"{asset_type}-{index:06d}"
        family, types = random.choice(config['families'])
        type_name = random.choice(types)
        level = random.choice(self.LEVELS)

        # Determine property key based on asset type
        property_key = asset_type.rstrip('s') + 'Properties'
        if asset_type == 'mepComponents':
            property_key = 'hvacProperties'
        elif asset_type == 'structuralElements':
            property_key = 'structuralProperties'

        asset = {
            "modelId": self.model_id,
            "id": asset_id,
            "type": config['type'],
            "space": {"id": f"space-building-{level.lower().replace(' ', '-')}"},
            "attributes": {
                "system": {
                    "uniqueId": self.generate_uuid(asset_type, index)
                }
            },
            "components": {
                "insertions": {
                    "metadata": {
                        "typeId": "autodesk.revit:element-metadata-1.0.0",
                        "staticChildren": {
                            "elementId": {"typeId": "String", "value": str(config['element_id_start'] + index)},
                            "categoryId": {"typeId": "String", "value": config['category']}
                        }
                    },
                    property_key: {
                        "typeId": f"autodesk.revit:{property_key.replace('Properties', '-properties')}-1.0.0",
                        "staticChildren": {
                            "familyName": {"typeId": "String", "value": family},
                            "typeName": {"typeId": "String", "value": type_name},
                            "level": {"typeId": "String", "value": level}
                        }
                    },
                    "geometry": {
                        "typeId": "autodesk.geometry:bounds-1.0.0",
                        "staticChildren": {
                            "minPoint": {"typeId": "Point3d", "value": self.generate_point3d()},
                            "maxPoint": {"typeId": "Point3d", "value": self.generate_point3d()}
                        }
                    },
                    "properties": {
                        "typeId": "autodesk.aec:component.propertyGroup-1.1.0",
                        "staticChildren": {
                            "properties": {
                                "typeId": "map<autodesk.parameter:parameter-2.0.0>",
                                "insertions": {}
                            }
                        }
                    }
                }
            }
        }

        return asset

    def generate_assets(self) -> List[Dict]:
        """Generate all assets according to distribution."""
        print(f"Generating {self.total_assets} assets...")

        assets = []

        # Calculate proportional distribution
        total_default = sum(config['count'] for config in self.ASSET_TYPES.values())

        for asset_type, config in self.ASSET_TYPES.items():
            # Calculate proportional count
            proportion = config['count'] / total_default
            count = int(self.total_assets * proportion)

            # Ensure at least some of each type if total_assets is large enough
            if count == 0 and self.total_assets >= len(self.ASSET_TYPES):
                count = 1

            print(f"  Generating {count} {asset_type}...")

            for i in range(count):
                if asset_type == 'walls':
                    asset = self.generate_wall(i, config)
                elif asset_type == 'doors':
                    asset = self.generate_door(i, config)
                elif asset_type == 'windows':
                    asset = self.generate_window(i, config)
                elif asset_type == 'rooms':
                    asset = self.generate_room(i, config)
                else:
                    asset = self.generate_generic_asset(asset_type, i, config)

                assets.append(asset)
                self.asset_ids_by_type[asset_type].append(asset['id'])

        self.generated_assets = assets
        print(f"Generated {len(assets)} assets")
        return assets

    def generate_relationships(self) -> List[Dict]:
        """Generate relationships between assets."""
        print(f"Generating {self.total_relationships} relationships...")

        relationships = []

        # Relationship types and their configurations
        rel_configs = [
            {
                'type': 'hosted',
                'from_types': ['doors', 'windows'],
                'to_types': ['walls'],
                'rel_type': 'autodesk.revit:hosted-1.0.0',
                'weight': 0.4
            },
            {
                'type': 'roomBounding',
                'from_types': ['rooms'],
                'to_types': ['walls'],
                'rel_type': 'autodesk.revit:roomBounding-1.0.0',
                'weight': 0.3
            },
            {
                'type': 'serves',
                'from_types': ['mepComponents'],
                'to_types': ['rooms'],
                'rel_type': 'autodesk.mep:serves-1.0.0',
                'weight': 0.2
            },
            {
                'type': 'contains',
                'from_types': ['rooms'],
                'to_types': ['furniture', 'fixtures'],
                'rel_type': 'autodesk.revit:contains-1.0.0',
                'weight': 0.1
            }
        ]

        for i in range(self.total_relationships):
            # Select relationship config based on weights
            config = random.choices(rel_configs, weights=[c['weight'] for c in rel_configs])[0]

            # Select random assets
            from_type = random.choice(config['from_types'])
            to_type = random.choice(config['to_types'])

            if not self.asset_ids_by_type[from_type] or not self.asset_ids_by_type[to_type]:
                continue

            from_asset = random.choice(self.asset_ids_by_type[from_type])
            to_asset = random.choice(self.asset_ids_by_type[to_type])

            relationship = {
                "modelId": self.model_id,
                "id": f"rel-{config['type']}-{i:06d}",
                "type": config['rel_type'],
                "from": {"assetId": from_asset},
                "to": {"assetId": to_asset},
                "attributes": {
                    "application": {
                        "relationshipType": config['type']
                    }
                }
            }

            # Add insertion point for hosted relationships
            if config['type'] == 'hosted':
                relationship['attributes']['application']['insertionPoint'] = self.generate_point3d()

            relationships.append(relationship)

        print(f"Generated {len(relationships)} relationships")
        return relationships

    def calculate_statistics(self, assets: List[Dict]) -> Dict:
        """Calculate model statistics."""
        total_size_bytes = len(json.dumps(assets, indent=2).encode('utf-8'))
        avg_asset_size = total_size_bytes / len(assets) if assets else 0

        # Count by type
        distribution = {}
        for asset_type in self.ASSET_TYPES.keys():
            distribution[asset_type] = len(self.asset_ids_by_type[asset_type])

        return {
            "totalEntities": len(assets),
            "modelSize": f"{total_size_bytes / (1024*1024):.2f}MB",
            "averageAssetSize": f"{avg_asset_size / 1024:.2f}KB",
            "batchCount": (len(assets) + 24) // 25,  # 25 entities per batch
            "entitiesPerBatch": 25
        }, distribution

    def generate_payload(self, output_dir: str = "aec_output"):
        """Generate collection files for model, assets, and relationships."""
        print("=" * 60)
        print("AEC Payload Generator - Collection Files")
        print("=" * 60)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate assets
        assets = self.generate_assets()

        # Generate relationships
        relationships = self.generate_relationships()

        # Calculate statistics
        stats, distribution = self.calculate_statistics(assets)

        # Create model document
        model_doc = {
            "modelId": self.model_id,
            "batchId": f"batch-aec-model-{self.total_assets}-entities",
            "description": f"AEC Model with {self.total_assets} entities - Generated payload",
            "modelStatistics": stats,
            "entityDistribution": distribution,
            "generationInfo": {
                "generatedAt": datetime.now().isoformat(),
                "generator": "AECPayloadGenerator v2.0",
                "totalAssets": len(assets),
                "totalRelationships": len(relationships),
                "outputFormat": "collection-files"
            }
        }

        # Save model document
        print(f"\nSaving model document...")
        model_file = output_path / "model.json"
        with open(model_file, 'w') as f:
            json.dump(model_doc, f, indent=2)
        model_size = model_file.stat().st_size / 1024
        print(f"✓ Model saved: {model_file} ({model_size:.2f}KB)")

        # Transform assets: move modelId and id to _id compound key
        print(f"\nTransforming {len(assets)} assets...")
        transformed_assets = []
        for asset in assets:
            transformed_asset = {
                "_id": {
                    "modelId": asset["modelId"],
                    "id": asset["id"]
                }
            }
            # Copy all fields except modelId and id
            for key, value in asset.items():
                if key not in ["modelId", "id"]:
                    transformed_asset[key] = value
            transformed_assets.append(transformed_asset)

        # Save all assets in a single file (JSON array)
        print(f"Saving {len(transformed_assets)} assets to single file...")
        assets_file = output_path / "assets.json"
        with open(assets_file, 'w') as f:
            json.dump(transformed_assets, f, indent=2)
        assets_size = assets_file.stat().st_size / (1024 * 1024)
        print(f"✓ Assets saved: {assets_file} ({assets_size:.2f}MB)")

        # Transform relationships: move modelId, from.assetId, to.assetId to _id compound key
        print(f"\nTransforming {len(relationships)} relationships...")
        transformed_relationships = []
        for rel in relationships:
            transformed_rel = {
                "_id": {
                    "modelId": rel["modelId"],
                    "fromAssetId": rel["from"]["assetId"],
                    "toAssetId": rel["to"]["assetId"]
                }
            }
            # Copy all fields except modelId, id, and update from/to to remove assetId
            for key, value in rel.items():
                if key in ["modelId", "id"]:  # Skip modelId and id (both moved to _id)
                    continue
                elif key == "from":
                    # Keep from object but without assetId (if there are other fields)
                    from_copy = {k: v for k, v in value.items() if k != "assetId"}
                    if from_copy:  # Only include if there are other fields
                        transformed_rel["from"] = from_copy
                elif key == "to":
                    # Keep to object but without assetId (if there are other fields)
                    to_copy = {k: v for k, v in value.items() if k != "assetId"}
                    if to_copy:  # Only include if there are other fields
                        transformed_rel["to"] = to_copy
                else:
                    transformed_rel[key] = value
            transformed_relationships.append(transformed_rel)

        # Save all relationships in a single file (JSON array)
        print(f"Saving {len(transformed_relationships)} relationships to single file...")
        relationships_file = output_path / "relationships.json"
        with open(relationships_file, 'w') as f:
            json.dump(transformed_relationships, f, indent=2)
        relationships_size = relationships_file.stat().st_size / (1024 * 1024)
        print(f"✓ Relationships saved: {relationships_file} ({relationships_size:.2f}MB)")

        # Create summary
        print("\n" + "=" * 60)
        print("✓ Generation complete!")
        print(f"  Output directory: {output_path}")
        print(f"\n  Files created:")
        print(f"    - model.json ({model_size:.2f}KB)")
        print(f"    - assets.json ({assets_size:.2f}MB, {len(assets)} documents)")
        print(f"    - relationships.json ({relationships_size:.2f}MB, {len(relationships)} documents)")
        print(f"\n  Entity Distribution:")
        for entity_type, count in distribution.items():
            print(f"    {entity_type}: {count}")
        print("\n  Import to MongoDB:")
        print(f"    mongoimport --db=<db_name> --collection=models --file=model.json")
        print(f"    mongoimport --db=<db_name> --collection=assets --file=assets.json --jsonArray")
        print(f"    mongoimport --db=<db_name> --collection=relationships --file=relationships.json --jsonArray")
        print("=" * 60)

        return model_doc, assets, relationships


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate AEC model payloads as individual MongoDB documents',
        epilog='Example: python3 aec_payload_generator.py --assets 5000 --relationships 1000 --output-dir my_model'
    )
    parser.add_argument('--assets', type=int, default=10000,
                       help='Number of assets to generate (default: 10000)')
    parser.add_argument('--relationships', type=int, default=2000,
                       help='Number of relationships to generate (default: 2000)')
    parser.add_argument('--output-dir', type=str, default='aec_output',
                       help='Output directory path (default: aec_output)')
    parser.add_argument('--model-id', type=str, default=None,
                       help='Model ID (default: auto-generated timestamp)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")

    generator = AECPayloadGenerator(
        total_assets=args.assets,
        total_relationships=args.relationships,
        model_id=args.model_id
    )

    generator.generate_payload(output_dir=args.output_dir)


if __name__ == '__main__':
    main()
