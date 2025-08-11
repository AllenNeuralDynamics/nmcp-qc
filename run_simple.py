import json

from aind.nmcp.process_qc import process


if __name__ == '__main__':
    with open("./aind-nmcp/tests/test_data/small_reconstruction.json", "r") as f:
        contents = f.read()

    output = process("609281", json.loads(contents))

    print(output)
