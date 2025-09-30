import json
import os

from aind.nmcp.process_qc import process_json, process_swc

if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))

    input_file = os.path.join(current_directory, "../aind-nmcp/tests/test_data/small_reconstruction.json")

    if input_file.endswith(".swc"):
        output = process_swc("609281", input_file)
    else:
        with open(input_file, "r") as f:
            contents = f.read()

        output = process_json("609281", json.loads(contents))

    print(output)
