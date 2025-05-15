FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends plantuml graphviz git curl && \
    curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get purge -y --auto-remove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Building the Solace Agent Mesh package
WORKDIR /sam-temp
COPY . /sam-temp
RUN python3.11 -m pip install --no-cache-dir hatch
RUN python3.11 -m hatch build

# Install the Solace Agent Mesh package
RUN python3.11 -m pip install --no-cache-dir dist/solace_agent_mesh-*.whl

# Clean up temporary files
WORKDIR /app
RUN rm -rf /sam-temp

# Create a non-root user
# RUN groupadd -r samapp && useradd -r -g samapp samapp
# RUN chown -R samapp:samapp /app /tmp

# # Switch to non-root user
# USER samapp

LABEL org.opencontainers.image.source=https://github.com/SolaceLabs/solace-agent-mesh

# CLI entry point
ENTRYPOINT ["solace-agent-mesh"]
