FROM python:3.6

# Install dependencies

RUN pip install --upgrade pip

COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt

# CMD ["sh", "run.bash"]