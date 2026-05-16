import json
import urllib.request
from flask import current_app
from backend.models import IntegrationConfig


def _post_webhook(url, payload):
    if not url:
        return False
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception as exc:
        print(f'[WorkNet Integration] {exc}')
        return False


def get_workspace_integrations(workspace):
    if not workspace:
        return None
    config = workspace.integrations
    if not config:
        return None
    return config


def broadcast_event(workspace, text, title='WorkNet Update'):
    config = get_workspace_integrations(workspace)
    if not config:
        return

    slack_url = config.slack_webhook or current_app.config.get('SLACK_WEBHOOK_DEFAULT')
    teams_url = config.teams_webhook or current_app.config.get('TEAMS_WEBHOOK_DEFAULT')

    if slack_url:
        _post_webhook(slack_url, {'text': f'*{title}*\n{text}'})
    if teams_url:
        _post_webhook(teams_url, {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            'summary': title,
            'themeColor': '1C8B7C',
            'title': title,
            'text': text,
        })
