# nmcp-qc
NMCP quality control services.

The package installs under the `aind.nmcp.qc` namespace:

- `aind.nmcp.qc` — QC library (`process_qc`) plus the FastAPI app (`main`).
- `aind.nmcp.qc.tools.process_file` — CLI for running QC against a file.

## Development

Run the API in dev mode (auto-reload):

```bash
uv run fastapi dev src/aind/nmcp/qc/main.py --port 5000
```

Run the file QC tool on a `.swc` or `.json` reconstruction. It prints the same JSON response the API returns:

```bash
uv run nmcp-qc-process path/to/reconstruction.swc --id 648434
```

Options:

- `--registered` — the reconstruction is CCF-registered: QC runs in CCF space with the post-registration suite,
  which adds the CCF mesh checks (`soma_inside_ccf_mesh`, `nodes_outside_ccf_mesh`). The first such run in a
  process loads the 10 µm CCF atlas, which costs ~4.8 GB of RAM (~9.4 GB peak). Without it, QC runs in image
  space with the pre-registration suite.
- `--skeleton <source>`, `--segments <id> [<id> ...]`, `--image <source>` — neuroglancer sources added to each
  metric's reference link.

## API

`POST /performqc/` takes the reconstruction id, its nodes and these optional fields:

| Field | Default | Meaning |
| --- | --- | --- |
| `isRegistered` | `false` | The reconstruction is CCF-registered; same effect and memory cost as `--registered`. |
| `skeletonSource` | `null` | Neuroglancer skeleton source for metric links. |
| `segmentIds` | `null` | Skeleton segment ids for metric links. |
| `imageSource` | `null` | Neuroglancer image source for metric links. |

camelCase is the documented form; snake_case field names are accepted too.

The response (and the CLI output) carries:

- `serviceVersion` and `standardMorphVersion`, the installed versions;
- `reconstructionId`;
- `qualityControl`, the aind-data-schema `QualityControl` document (the AIND QC portal's `qc.json`) built by
  standard-morph, or `null` when the service failed;
- `error`, `null` on success, otherwise `{stage, kind, description, info}` with `stage` one of `input`,
  `standard_morph` or `output`.

Problems standard-morph finds in the reconstruction are reported inside `qualityControl` as failed or pending
metrics, not as an `error`.

## Tests

```bash
uv run pytest
```

The real-atlas test is excluded by default; run it with `uv run pytest -m atlas` (needs ~10 GB of free RAM).

## Docker

`task build` builds the wheel and the image; `task release` also pushes the image. The
container runs `docker-entry.sh`, which launches the installed `nmcp-qc-serve`
console script (uvicorn on port 5000). Host/port can be overridden with the
`NMCP_QC_HOST` / `NMCP_QC_PORT` environment variables.
