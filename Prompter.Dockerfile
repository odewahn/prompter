#first stage - builder
FROM python:3.9-slim as builder
COPY . /prompter
WORKDIR /prompter
RUN apt-get update && apt-get install -y binutils
RUN pip install -r requirements.txt
RUN pyinstaller --noconfirm --clean prompter.spec

#second stage
FROM python:3.9-slim
RUN apt-get update && apt-get install -y 'ffmpeg' 
COPY --from=builder /prompter/dist/prompter /usr/local/bin/prompter
RUN chmod +x /usr/local/bin/prompter
RUN mkdir /app
WORKDIR /app