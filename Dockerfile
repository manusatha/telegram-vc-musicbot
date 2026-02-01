FROM python:3.10-slim
WORKDIR /app
RUN apt update && apt install -y ffmpeg
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
