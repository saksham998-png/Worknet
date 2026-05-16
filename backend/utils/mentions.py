import re
from models import User, Mention, Notification, db


MENTION_PATTERN = re.compile(r'@([a-zA-Z0-9_]+)')


def parse_mentions(content, project):
    usernames = set(MENTION_PATTERN.findall(content))
    if not usernames:
        return []
    members = {m.username.lower(): m for m in project.members}
    return [members[u.lower()] for u in usernames if u.lower() in members]


def process_mentions(comment, project, author):
    mentioned_users = parse_mentions(comment.content, project)
    for user in mentioned_users:
        if user.id == author.id:
            continue
        db.session.add(Mention(comment=comment, mentioned_user=user))
        db.session.add(Notification(
            user=user,
            title=f'{author.username} mentioned you',
            message=comment.content[:200],
            link=f'/projects/{project.id}',
        ))
    return mentioned_users
