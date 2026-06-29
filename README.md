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

Run the file QC tool:

```bash
uv run nmcp-qc-process path/to/reconstruction.swc --id 648434
```

Run the tests:

```bash
uv run --with pytest pytest tests
```

## Docker

`task build` builds the wheel and the image; `task release` also pushes the image. The
container runs `docker-entry.sh`, which launches the installed `nmcp-qc-serve`
console script (uvicorn on port 5000). Host/port can be overridden with the
`NMCP_QC_HOST` / `NMCP_QC_PORT` environment variables.
