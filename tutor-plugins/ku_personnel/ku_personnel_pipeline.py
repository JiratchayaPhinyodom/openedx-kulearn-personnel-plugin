import requests

def save_organizations(user, social=None, *args, **kwargs):
    if social:
        resp = requests.get(
            "https://people.googleapis.com/v1/people/me",
            params={
                'access_token': social.extra_data['access_token'],
                'personFields': "organizations",
            }
        )
        try:
            data = resp.json()
            if 'organizations' in data:
                social.extra_data['organizations'] = data['organizations']
                social.save()
        except Exception:
            pass
    return None