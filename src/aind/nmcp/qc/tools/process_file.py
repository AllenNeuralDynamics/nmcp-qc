import argparse
import json

from aind.nmcp.qc.process_qc import process_json, process_swc_file


def main():
    parser = argparse.ArgumentParser(
        description="Run NMCP quality control on a reconstruction file (.swc or .json)."
    )
    parser.add_argument("input_file", help="Path to a .swc or .json reconstruction file.")
    parser.add_argument(
        "--id",
        dest="reconstruction_id",
        default="unknown",
        help="Reconstruction id used to label the output.",
    )
    args = parser.parse_args()

    if args.input_file.endswith(".swc"):
        output = process_swc_file(args.reconstruction_id, args.input_file)
    else:
        with open(args.input_file, "r") as f:
            output = process_json(args.reconstruction_id, json.load(f))

    print(output)


if __name__ == "__main__":
    main()
