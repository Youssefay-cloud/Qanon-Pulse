FROM ghcr.io/ggml-org/llama.cpp:server

# Switch to root to install curl and create folders
USER root

# Try apt-get (Debian) first, or apk (Alpine) depending on the base image. 
# Most Llama.cpp images use Debian slim or Alpine.
RUN apt-get update && apt-get install -y curl || apk add --no-cache curl

# Download the model inside the container
RUN mkdir -p /models && \
    curl -L -o /models/Qwen3.5-0.8B-Q4_0.gguf "https://huggingface.co/Qwen/Qwen3.5-0.8B-GGUF/resolve/main/Qwen3.5-0.8B-Q4_0.gguf"

# Run the server (this matches the CMD from the original image)
CMD ["-m", "/models/Qwen3.5-0.8B-Q4_0.gguf", "--host", "0.0.0.0", "--port", "8080", "-c", "4096"]