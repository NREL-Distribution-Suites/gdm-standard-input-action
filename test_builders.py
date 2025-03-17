from pathlib import Path
import json
from jsonschema import validate
from catalogs.build_catalogs import build_catalog

root_path = Path(__file__).parent 
schema_folder = root_path / "schema"
catlog_schema_file = schema_folder / "catalog_system.json"
distribution_schema_file = schema_folder / "distribution_system.json"

opendss_folder = root_path / "opendss"
master_file_name = "Master.dss"
doc_file_name = "doc.json"

catalog_folder = root_path / "catalogs"

def test_opendss_model_has_master_file():
    for path in opendss_folder.iterdir():
        master_file = path / master_file_name
        assert master_file.exists()

def test_doc_json_file_exists():
    for path in opendss_folder.iterdir():
        doc_file = path / doc_file_name
        assert doc_file.exists() 

def read_json_file(json_file: Path) -> dict:
    with open(json_file, "r", encoding="utf-8") as f:
        schema = json.load(f)   
    return schema

def get_distribution_system_schema():
    return read_json_file(distribution_schema_file)

def get_catalog_system_schema():
    return read_json_file(catlog_schema_file)

def test_validate_doc_json_schema():
    schema = get_distribution_system_schema()
    for path in opendss_folder.iterdir():
        doc_file = path / doc_file_name
        validate(instance=read_json_file(doc_file), schema=schema)

def test_validate_catalog_doc_json_schema():
    doc_file = catalog_folder / doc_file_name
    validate(instance=read_json_file(doc_file), schema=get_catalog_system_schema())

def test_catalog_build():
    build_catalog()