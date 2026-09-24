#!/usr/bin/env bash
# Environment installation meant to be executed inside Google Colab
pip install fastapi uvicorn pydantic httpx torch
wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb > /dev/null 2>&1
