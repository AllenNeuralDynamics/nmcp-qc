FROM python:3.10

WORKDIR /wheel

COPY wheel/standard_morph-0.1.0-py3-none-any.whl ./
RUN pip install ./standard_morph-0.1.0-py3-none-any.whl

COPY wheel/aind_neuron_reconstruction_io-0.0.0-py3-none-any.whl ./
RUN pip install ./aind_neuron_reconstruction_io-0.0.0-py3-none-any.whl

COPY aind-nmcp/dist/nmcpqc-1.0.0-py3-none-any.whl ./
RUN pip install ./nmcpqc-1.0.0-py3-none-any.whl

WORKDIR /app

COPY app/main.py ./

COPY docker-entry.sh ./

COPY app/*.* .

CMD ["./docker-entry.sh"]
