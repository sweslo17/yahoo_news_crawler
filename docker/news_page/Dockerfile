FROM python:3.7

COPY requirements.txt /

RUN pip3 install --no-cache-dir -r /requirements.txt && rm /requirements.txt

CMD ["python", "crawl_news_page.py"]

COPY . /