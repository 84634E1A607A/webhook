FROM python:3.12

WORKDIR /app

RUN apt update\
  && apt install git git-lfs ssh -y

COPY requirements.txt .

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
	-r ./requirements.txt

COPY . .

CMD ["sh", "startup.sh"]
