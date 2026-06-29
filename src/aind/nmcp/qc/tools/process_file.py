import argparse

from aind.nmcp.qc.process_qc import process_json_file, process_swc_file
from aind.nmcp.qc.reconstruction_input import QualityControlOptions


def main():
    parser = argparse.ArgumentParser(
        description="Run NMCP quality control on a reconstruction file (.swc or .json) and print the result as JSON."
    )
    parser.add_argument("input_file", help="Path to a .swc or .json reconstruction file.")
    parser.add_argument(
        "--id",
        dest="reconstruction_id",
        default="unknown",
        help="Reconstruction id used to label the output.",
    )
    parser.add_argument(
        "--registered",
        dest="is_registered",
        action="store_true",
        help="The reconstruction is CCF-registered: run in CCF space and add the CCF mesh checks, which load the "
             "10 µm CCF atlas (~4.8 GB resident, ~9.4 GB peak). Without it, QC runs in image space.",
    )
    parser.add_argument("--skeleton", dest="skeleton_source", help="Neuroglancer skeleton source for metric links.")
    parser.add_argument("--segments", dest="segment_ids", nargs="+", help="Skeleton segment ids for metric links.")
    parser.add_argument("--image", dest="image_source", help="Neuroglancer image source for metric links.")
    args = parser.parse_args()

    options = QualityControlOptions(
        is_registered=args.is_registered,
        skeleton_source=args.skeleton_source,
        segment_ids=args.segment_ids,
        image_source=args.image_source,
    )

    if args.input_file.endswith(".swc"):
        output = process_swc_file(args.reconstruction_id, args.input_file, options)
    else:
        output = process_json_file(args.reconstruction_id, args.input_file, options)

    print(output.model_dump_json(by_alias=True, indent=2))


if __name__ == "__main__":
    main()
