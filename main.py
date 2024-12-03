from pathlib import Path
import importlib.metadata
import os 
import json
import traceback
from uuid import uuid4
import shutil

from ditto.readers.opendss.reader import Reader

def change_permissions_recursively(folder_path):
    """
    Change permissions of a folder and all its contents recursively.

    Args:
        folder_path (str): Path to the folder.
        mode (int): The permissions to set (default is 0o755).
    """
    for root, dirs, files in os.walk(folder_path):
        # Change permissions for directories
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            os.chmod(dir_path, 0o777)
        
        # Change permissions for files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, 0o666)
    
    # Change permissions for the top-level folder itself
    os.chmod(folder_path, 0o777)

def process_opendss_models(opendss_paths: list[Path], output_path: Path):
    gdm_version = get_gdm_version()
    new_output_path = output_path / gdm_version.replace(".", "_")
    if new_output_path.exists():
        shutil.rmtree(new_output_path)
    new_output_path.mkdir(parents=True, exist_ok=True)
    combined_doc = []
    for opendss_path in opendss_paths:
        with open(opendss_path.parent / "doc.json", "r", encoding="utf-8") as f:
            doc = json.load(f)
            combined_doc.append(doc)

        parent_folder = new_output_path / doc["name"]
        if parent_folder.exists():
            shutil.rmtree(parent_folder)
        parent_folder.mkdir(parents=True, exist_ok=True)

        json_file_name = opendss_path.parent.name + '.json'
        sys = Reader(opendss_path).get_system()
        sys.to_json(parent_folder/ json_file_name)
        
    with open(output_path / "doc.json", "w", encoding="utf-8") as f:
        json.dump(combined_doc, f, indent=4)

def get_gdm_version():
    gdm_version = importlib.metadata.version("grid-data-models")
    return gdm_version

def save_output(key: str, value: str, file_path: str):
    """Function to save output."""
    with open(file_path, "a", encoding="utf-8") as fh:
        print(f"{key}={value}", file=fh)

def save_multiline_output(key: str, value: str, file_path: str):
    """Function to save multi line output."""
    with open(file_path, "a", encoding="utf-8") as fh:
        delimiter = "EOF"
        print(f"{key}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)



if __name__ == '__main__':
    
    try:
        root_path = Path(__file__).parent / "opendss"
        datapath = os.environ["INPUT_DATAPATH"]
        output_file = os.environ["GITHUB_OUTPUT"]
        datapath = Path(datapath) / 'DistributionSystem'
        process_opendss_models(
            [
                file_path / 'Master.dss' for file_path in root_path.iterdir()
            ],
            datapath
        )
        change_permissions_recursively(datapath)
        save_output("branch", f"auto/{get_gdm_version()}_{str(uuid4())}", output_file)

    except Exception as _:
        save_multiline_output(
                "errormessage", traceback.format_exc(), output_file
            )