FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copiar os arquivos necessários
COPY recebercsv.py /app/recebercsv.py
COPY requirements.txt /app/requirements.txt

# Instalar as dependências
RUN pip install -r requirements.txt

# Comando padrão que permite argumentos
ENTRYPOINT ["python", "recebercsv.py"]
