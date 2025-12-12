from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, subprocess

app = FastAPI()

APP_DIR = os.environ.get("APP_DIR", "/home/ubuntu/app")
EXPECTED_TOKEN = os.environ.get("DEPLOY_TOKEN", "")

class DeployReq(BaseModel):
    blue_image: str
    green_image: str
    git_sha: str

def sh(cmd: str):
    return subprocess.run(cmd, shell=True, cwd=APP_DIR, check=True, capture_output=True, text=True)

@app.post("/deploy")
def deploy(req: DeployReq, authorization: str = Header(default="")):
    if not EXPECTED_TOKEN:
        raise HTTPException(500, "DEPLOY_TOKEN not set on server")
    if authorization != f"Bearer {EXPECTED_TOKEN}":
        return 401

    image_tag = req.git_sha

    sh(f"export IMAGE_TAG={image_tag} && docker compose -f docker-compose.blue.yml pull")
    sh(f"export IMAGE_TAG={image_tag} && docker compose -f docker-compose.green.yml pull")

    sh(f"export IMAGE_TAG={image_tag} && docker compose -f docker-compose.blue.yml up -d")
    sh(f"export IMAGE_TAG={image_tag} && docker compose -f docker-compose.green.yml up -d")

    sh("docker compose -f docker-compose.nginx.yml up -d")
    sh("docker exec nginx nginx -t")
    sh("docker exec nginx nginx -s reload")

    return {"status": "ok", "image_tag": image_tag}