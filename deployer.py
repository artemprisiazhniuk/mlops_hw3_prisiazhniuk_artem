from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, subprocess

app = FastAPI()

APP_DIR = os.environ.get("APP_DIR", "./")
EXPECTED_TOKEN = os.environ.get("DEPLOY_TOKEN", "")

class DeployReq(BaseModel):
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

    sh(f"export IMAGE_TAG={image_tag} && docker compose -f docker-compose.blue.yml -f docker-compose.green.yml -f docker-compose.nginx.yml up -d")
    sh("docker exec mlops_hw3_prisiazhniuk_artem-nginx-1 nginx -t")
    sh("docker exec mlops_hw3_prisiazhniuk_artem-nginx-1 nginx -s reload")

    return {"status": "ok", "image_tag": image_tag}