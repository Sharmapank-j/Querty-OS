FROM ubuntu:24.04

# Metadata
LABEL maintainer="Querty-OS Team"
LABEL description="Querty-OS - AI-First System Layer for Android"
LABEL version="0.1.0"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV QUERTY_HOME=/opt/querty-os
ENV QUERTY_DATA=/data/querty
ENV PATH="${QUERTY_HOME}/scripts:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Base utilities
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # Python and development
    python3.12 \
    python3.12-dev \
    python3-pip \
    python3-venv \
    # System tools
    psmisc \
    procps \
    iproute2 \
    net-tools \
    # Audio/Video (for input handlers)
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    # Android tools
    adb \
    fastboot \
    android-sdk-platform-tools \
    # Chroot and container tools
    debootstrap \
    schroot \
    # Wine dependencies (for Windows app support)
    wine \
    winetricks \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application directories
RUN mkdir -p ${QUERTY_HOME} ${QUERTY_DATA} \
    && mkdir -p ${QUERTY_DATA}/{ai,android,linux,windows,snapshots,logs}

# Set work directory
WORKDIR ${QUERTY_HOME}

# Copy application files
COPY . ${QUERTY_HOME}/

# Install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install -r requirements.txt && \
    pip3 install -e .

# Create necessary directories and set permissions
RUN mkdir -p /var/log && \
    touch /var/log/querty-ai-daemon.log && \
    chmod 666 /var/log/querty-ai-daemon.log

# Create non-root user for running the application
RUN useradd -m -u 1000 -s /bin/bash querty && \
    chown -R querty:querty ${QUERTY_HOME} ${QUERTY_DATA} /var/log/querty-ai-daemon.log

# Switch to non-root user
USER querty

# Expose ports (if needed for API/monitoring)
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 ${QUERTY_HOME}/scripts/utils/check-status.sh || exit 1

# Set entrypoint
ENTRYPOINT ["/opt/querty-os/scripts/boot/init-querty.sh"]

# Default command
CMD ["--mode=daemon"]
