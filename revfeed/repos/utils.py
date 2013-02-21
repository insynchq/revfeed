import hashlib


def gravatar(email):
    if getattr(gravatar, 'cache', False):
        url = gravatar.cache.get(email)
    else:
        gravatar.cache = {}
        url = None
    if not url:
        if email:
            email_hash = hashlib.md5(email).hexdigest()
        else:
            email_hash = '00000000000000000000000000000000'
        url = gravatar.cache[email] = (
            "https://gravatar.com/avatar/{0}?size=20".format(email_hash)
            )
    return url
