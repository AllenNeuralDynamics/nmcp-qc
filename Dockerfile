FROM python:3.10

WORKDIR /wheel

COPY aind-nmcp/dist/nmcpqc-3.0.3-py3-none-any.whl ./
RUN pip install ./nmcpqc-3.0.3-py3-none-any.whl

WORKDIR /app

COPY app/main.py ./

COPY docker-entry.sh ./

COPY app/*.* .

CMD ["./docker-entry.sh"]
