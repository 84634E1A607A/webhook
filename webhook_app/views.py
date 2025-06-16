from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import hmac
import hashlib
from .models import WebhookLog
import asyncio
import subprocess

async def clone_repository(repo_url, branch, target_dir):
    try:
        subprocess.run(
            ["git", "clone", "--branch", branch, repo_url, target_dir],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")

def handle_gitlab_push_event(payload, log: WebhookLog):
    repo_url = payload["repository"]["git_ssh_url"]
    branch = payload["ref"].split("/")[-1]
    dir_name = payload["project"]["path_with_namespace"].replace("/", "-")
    target_dir = f"/git/{dir_name}/{int(log.received_at.timestamp()*1000)}"
    log.path = target_dir
    log.save()
    asyncio.run(clone_repository(repo_url, branch, target_dir))

@csrf_exempt
def github_webhook(request):
    if request.method == 'POST':
        try:
            payload = request.body
            signature = request.headers.get('X-Hub-Signature')
            secret = b''  # Replace with your actual secret key
            verified = verify_signature(payload, signature, secret)

            # Log the request
            WebhookLog.objects.create(
                headers=json.dumps(dict(request.headers)),
                body=request.body.decode('utf-8'),
                verified=verified,
                source='github',
            )

            if not verified:
                return JsonResponse({'status': 'invalid signature'}, status=400)

            payload = json.loads(payload)

            # Process the payload here
            # if payload.get("hook") and payload["hook"]["type"] == "push":
                # handle_push_event(payload)

            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'invalid payload'}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
def gitlab_webhook(request):
    if request.method == 'POST':
        try:
            payload = request.body
            token = request.headers.get('X-Gitlab-Token')
            secreta = ''  # Replace with your actual secret key
            secretb = ''

            # Log the request
            log = WebhookLog.objects.create(
                headers=json.dumps(dict(request.headers)),
                body=request.body.decode('utf-8'),
                verified=(token == secreta or token == secretb),
                source='gitlab',
                comment=('Spring25a' if token == secreta else
                         'Spring25b' if token == secretb else ''),
            )

            if token != secreta and token != secretb:
                return JsonResponse({'status': 'invalid token'}, status=400)

            payload = json.loads(payload)

            # Process the payload here
            if payload.get("object_kind") == "push":
                handle_gitlab_push_event(payload, log)

            return JsonResponse({'status': 'success'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'invalid payload'}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)

def verify_signature(payload, signature, secret):
    try:
        hash_object = hmac.new(secret, payload, hashlib.sha1)
        expected_signature = 'sha1=' + hash_object.hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    except:
        return False
