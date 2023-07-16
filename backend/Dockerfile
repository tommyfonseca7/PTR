FROM python:latest AS builder
WORKDIR /backend
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:latest
EXPOSE 5000
COPY --from=builder /root/.local /root/.local
COPY . /backend
WORKDIR /backend
ENV PYTHONPATH=/backend
ENV PATH=/root/.local/bin:$PATH
CMD flask run --debug --host=0.0.0.0