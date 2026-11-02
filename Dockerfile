FROM python:3.12-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app \
    OPENBLAS_NUM_THREADS=2 \
    OMP_NUM_THREADS=2

# LightGBM's CPU wheels need OpenMP; signature/TLS verification stays enabled.
RUN --mount=type=secret,id=build_ca,required=false,mode=0444 \
    build_ca=/etc/ssl/certs/ca-certificates.crt \
    && if [ -r /run/secrets/build_ca ]; then build_ca=/run/secrets/build_ca; fi \
    && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -o APT::Update::Error-Mode=any -o Acquire::https::CaInfo="$build_ca" \
    && apt-get -o Acquire::https::CaInfo="$build_ca" install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY requirements.lock ./
RUN --mount=type=secret,id=build_ca,required=false,mode=0444 \
    build_ca=/etc/ssl/certs/ca-certificates.crt \
    && if [ -r /run/secrets/build_ca ]; then build_ca=/run/secrets/build_ca; fi \
    && pip install --cert "$build_ca" --no-cache-dir --require-hashes -r requirements.lock
COPY src ./src
COPY app ./app
COPY .streamlit ./.streamlit
# Bake in the trusted current release shipped on main; no startup training is needed.
COPY models ./models
# Repository files can be private (0600) in cloud checkouts. Make runtime assets
# readable by the unprivileged process, and remove write access to code/artifacts.
RUN chmod -R a=rX /app
USER appuser
EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3).read() == b'ok'"
CMD ["python", "-m", "streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
