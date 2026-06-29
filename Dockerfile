FROM python:3.11

WORKDIR /app

# Install the exact versions from uv.lock. --no-deps is required: uv.lock overrides
# aind-neuron-reconstruction-io's numpy==1.23.5 pin (see [tool.uv] in pyproject.toml), which
# pip's resolver would reject.
COPY dist/requirements.txt ./
RUN pip install --no-cache-dir --no-deps -r requirements.txt

COPY dist/nmcpqc-*-py3-none-any.whl ./
RUN pip install --no-cache-dir --no-deps ./nmcpqc-*-py3-none-any.whl

COPY docker-entry.sh ./
RUN chmod +x docker-entry.sh

CMD ["./docker-entry.sh"]
