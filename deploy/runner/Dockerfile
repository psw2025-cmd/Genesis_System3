FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg jq git openssh-client \
    python3 python3-pip unzip apt-transport-https \
    gnupg2 lsb-release wget \
    openssl procps uuid-runtime && \
    rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    > /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor \
    > /usr/share/keyrings/cloud.google.gpg && apt-get update && apt-get install -y google-cloud-sdk

# Install gh (GitHub CLI)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor \
    > /usr/share/keyrings/githubcli.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
    > /etc/apt/sources.list.d/github-cli.list && apt-get update && apt-get install -y gh

# Add helper tools
RUN pip3 install --no-cache-dir requests --break-system-packages

WORKDIR /workspace
COPY runbook-audit-schema.json /workspace/runbook-audit-schema.json
COPY entrypoint.sh /workspace/entrypoint.sh
RUN chmod +x /workspace/entrypoint.sh

ENTRYPOINT ["/workspace/entrypoint.sh"]
