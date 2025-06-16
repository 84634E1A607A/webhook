from django.db import models
import json

class WebhookLog(models.Model):
    headers = models.TextField()
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField()
    source = models.CharField(max_length=50, default="unknown")
    comment = models.TextField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        headers = json.loads(self.headers)
        
        try:
            body = json.loads(self.body)
        except json.JSONDecodeError:
            return "JSON_DECODE_ERROR"

        repo = "UNKNOWN"

        try:
            if self.source == "github":
                repo = body["repository"]["full_name"]
            elif self.source == "gitlab":
                if "project" in body:
                    repo = body["project"]["path_with_namespace"]
                elif "path_with_namespace" in body:
                    repo = body["path_with_namespace"]
        except:
            repo = "UNKNOWN"
        
        try:
            if self.source == "github":
                event = headers["X-Github-Event"]
            elif self.source == "gitlab":
                event = headers["X-Gitlab-Event"]
                event_name = body.get("object_kind", "unknown")
                event_name = event_name if event_name != "unknown" else body.get("event_name", "unknown")
                event = f"{event} ({event_name}) [{self.comment}]"
            else:
                event = "UNKNOWN"
        except:
            event = "ERROR"

        return f'{self.received_at.astimezone().strftime("%m/%d %H:%M:%S")} - {repo} - {event}' + (" - UNVERIFIED" if not self.verified else "")

