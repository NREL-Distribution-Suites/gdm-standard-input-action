from pathlib import Path
import json
from jsonschema import validate


def test_opendss_model_has_master_file():
    root_path = Path(__file__).parent / "opendss"
    for path in root_path.iterdir():
        master_file = path / "Master.dss"
        assert master_file.exists()

def test_doc_json_file_exists():
    root_path = Path(__file__).parent / "opendss"
    for path in root_path.iterdir():
        doc_file = path / "doc.json"
        assert doc_file.exists() 

def test_validate_doc_json_schema():
    root_path = Path(__file__).parent / "opendss"
    schema_file = Path(__file__).parent / "schema" / "distribution_system.json"
    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)    
    for path in root_path.iterdir():
        doc_file = path / "doc.json"
        with open(doc_file, "r",encoding="utf-8") as f:
            data = json.load(f)
            validate(instance=data, schema=schema)
        
        