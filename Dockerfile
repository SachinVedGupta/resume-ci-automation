FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra texlive-fonts-recommended git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN uv sync --locked
CMD ["uv", "run", "python", "-m", "resume_ci_automation", "--all"]
