from pathlib import Path
import importlib.metadata
import os 
import traceback
from uuid import uuid4

from ditto.readers.opendss.reader import Reader

def process_opendss_models(opendss_paths: list[Path], output_path: Path):
    gdm_version = importlib.metadata.version("grid-data-models")
    for opendss_path in opendss_paths:
        json_file_name = opendss_path.stem + '.json'
        output_path = output_path / gdm_version / json_file_name
        sys = Reader(opendss_path).get_system()
        sys.to_json(output_path)

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
        gdm_version = importlib.metadata.version("grid-data-models")
        save_output("branch", f"auto/{gdm_version}_{str(uuid4())}", output_file)

    except Exception as _:
        save_multiline_output(
                "errormessage", traceback.format_exc(), output_file
            )