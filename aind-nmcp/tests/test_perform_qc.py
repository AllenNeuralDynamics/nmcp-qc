import json
from pathlib import Path

from aind.nmcp.process_qc import process_json


def test_process_qc():
    this_dir = Path(__file__).parent.resolve()

    with open(this_dir.joinpath("test_data").joinpath("small_reconstruction.json"), "r") as f:
        contents = f.read()

    output = process_json("123456", json.loads(contents))

    assert output.reconstruction_id == "123456"


if __name__ == '__main__':
    test_process_qc()
