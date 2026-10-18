FROM python:3.12-slim
LABEL org.opencontainers.image.title="Docker Command Reference" \
      org.opencontainers.image.description="Docker commands and one-line descriptions, served as plain text for curl" \
      org.opencontainers.image.source="https://github.com/thrishaldoma/docker-command-reference"
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8080
WORKDIR /app
COPY server.py commands.txt flags.txt examples.txt catalog.json /app/
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8080/healthz', headers={'User-Agent':'curl/healthcheck'}), timeout=2).read()"
CMD ["python", "server.py"]
