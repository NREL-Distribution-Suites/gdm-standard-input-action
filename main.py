from pathlib import Path
import importlib.metadata
import os 
import traceback
from uuid import uuid4

from ditto.readers.opendss.reader import Reader

def change_permissions_recursively(folder_path, mode=0o755):
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
            os.chmod(dir_path, mode)
        
        # Change permissions for files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            os.chmod(file_path, mode)
    
    # Change permissions for the top-level folder itself
    os.chmod(folder_path, mode)

def process_opendss_models(opendss_paths: list[Path], output_path: Path):
    gdm_version = importlib.metadata.version("grid-data-models")
    for opendss_path in opendss_paths:
        json_file_name = opendss_path.parent.name + '.json'
        output_path = output_path / gdm_version.replace(".", "_")
        output_path.mkdir(parents=True, exist_ok=True)
        sys = Reader(opendss_path).get_system()
        sys.to_json(output_path/ json_file_name)

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
        process_opendss_models(
            [
                root_path / "p5r/Master_pv.dss"
            ],
            Path(datapath)
        )
        change_permissions_recursively(datapath)
        gdm_version = importlib.metadata.version("grid-data-models")
        save_output("branch", f"auto/{gdm_version}_{str(uuid4())}", output_file)

    except Exception as _:
        save_multiline_output(
                "errormessage", traceback.format_exc(), output_file
            )