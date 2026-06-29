FROM python:3.10

WORKDIR /app

COPY dist/nmcpqc-*-py3-none-any.whl ./
RUN pip install ./nmcpqc-*-py3-none-any.whl

COPY docker-entry.sh ./
RUN chmod +x docker-entry.sh

CMD ["./docker-entry.sh"]
