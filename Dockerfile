# docker build -t caitest .
# docker run -it caitest

FROM ubuntu:24.04

# Set DEBIAN_FRONTEND to noninteractive to avoid prompts during apt-get install
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git python3-pip python3.12-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a directory for the application
WORKDIR /app

# Copy only necessary files (respecting .dockerignore)
COPY . /app/

# Create and activate virtual environment, then install the package
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -U pip && \
    /app/venv/bin/pip install --no-cache-dir .

# Set the default command to run the CAI CLI tool
# Update this to the actual command you want to run, e.g., cai --version or cai --help
CMD ["/app/venv/bin/cai", "--help"]
