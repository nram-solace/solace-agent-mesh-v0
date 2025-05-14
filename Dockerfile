FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends plantuml graphviz git && \
    apt-get purge -y --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installing the Solace Agent Mesh package
RUN python3.11 -m pip install --no-cache-dir solace-agent-mesh

# Create a non-root user
RUN groupadd -r samapp && useradd -r -g samapp samapp
RUN chown -R samapp:samapp /app /tmp

# Switch to non-root user
USER samapp

LABEL org.opencontainers.image.source https://github.com/SolaceLabs/solace-agent-mesh

# CLI entry point
ENTRYPOINT ["solace-agent-mesh"]
