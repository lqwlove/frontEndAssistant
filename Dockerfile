FROM python:3.11.10

WORKDIR /aiserver

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "src.Server"]