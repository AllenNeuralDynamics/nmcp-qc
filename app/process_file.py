import json
import os

from aind.nmcp.process_qc import process_json, process_swc_file

if __name__ == '__main__':
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # input_file = os.path.join(current_directory, "../aind-nmcp/tests/test_data/small_reconstruction.json")
    input_file = r"C:\Work\aind\nmcp\data\lc-dataset-04-2026-v1\648434-ccf\swc\N004-648434-CONSENSUS.swc"

    if input_file.endswith(".swc"):
        output = process_swc_file("648434", input_file)
    else:
        with open(input_file, "r") as f:
            contents = f.read()

        output = process_json("609281", json.loads(contents))

    print(output)
