## ✅ Complete Tutor Plugin: `ku_personnel`

Here is the full structure with everything you need:

---

### 📁 `~/.local/share/tutor-plugins/ku_personnel.py`

```python
import os
from tutor import hooks

# Inject your function into the SOCIAL_AUTH_PIPELINE
hooks.Filters.ENV_PATCHES.add_item((
    "openedx-lms-common-settings",
    """
# KU Personnel OAuth pipeline
SOCIAL_AUTH_PIPELINE += ('ku_personnel.ku_personnel_pipeline.save_organizations',)
    """
))

# Optional init message for confirmation
hooks.Filters.CLI_DO_INIT_TASKS.add_item((
    "ku_personnel",
    """
echo "++++++ Initializing KU Personnel plugin"
    """
))

# Mount ku_personnel directory to edx-platform (LMS/CMS)
plugin_dir = os.path.join(os.path.dirname(__file__), "ku_personnel")

if os.path.isdir(plugin_dir):
    hooks.Filters.MOUNT_LMS_STATIC.add_item((plugin_dir, "/openedx/edx-platform/ku_personnel"))
    hooks.Filters.MOUNT_CMS_STATIC.add_item((plugin_dir, "/openedx/edx-platform/ku_personnel"))
```

---

### 📁 `~/.local/share/tutor-plugins/ku_personnel/ku_personnel_pipeline.py`

```python
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
```

---

### 📁 `~/.local/share/tutor-plugins/ku_personnel/ku_personnel_task.py`

```python
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from cms.djangoapps.course_creators.models import CourseCreator
from cms.djangoapps.course_creators.views import add_user_with_status_granted

from celery import task
from celery.utils.log import get_task_logger

LOGGER = get_task_logger(__name__)
LOG_PREFIX = "KU Learn"

def is_ku_personnel(user):
    try:
        social = user.social_auth.get(provider="google-oauth2")
        return social.extra_data['organizations'][0]['title'] == 'Personnel'
    except (UserSocialAuth.DoesNotExist, KeyError, IndexError):
        return False

@task(ignore_result=True)
def approve_course_creators():
    admin = User.objects.filter(is_superuser=True).first()
    pendings = CourseCreator.objects.filter(state=CourseCreator.PENDING)
    for req in pendings:
        user = req.user
        req.delete()
        if is_ku_personnel(user):
            add_user_with_status_granted(admin, user)
            LOGGER.info(f"[{LOG_PREFIX}] Granted course creator rights to {user.username}")
        else:
            LOGGER.info(f"[{LOG_PREFIX}] Denied course creator rights for {user.username}")
```

---

### 📁 `~/.local/share/tutor-plugins/ku_personnel/management/commands/validate_ku.py`

```python
from django.core.management.base import BaseCommand
from ku_personnel.ku_personnel_task import approve_course_creators

class Command(BaseCommand):
    help = 'Approve or deny course creator requests'

    def handle(self, *args, **kwargs):
        approve_course_creators.delay()
```

---

## ✅ How to Use with Tutor K8s

1. Copy all the files into:

   ```
   ~/.local/share/tutor-plugins/
   ├── ku_personnel.py
   └── ku_personnel/
       ├── ku_personnel_pipeline.py
       ├── ku_personnel_task.py
       └── management/
           └── commands/
               └── validate_ku.py
   ```

2. Enable and apply:

```bash
tutor plugins enable ku_personnel
tutor config save
tutor images build openedx  # if needed
tutor k8s upgrade
```

3. Test manually:

```bash
tutor k8s run lms ./manage.py validate_ku
```

4. (Optional) Add Kubernetes `CronJob` if you want auto-processing.

---

Would you like me to generate this as a `.zip` or `.tar.gz` you can download and extract into your Tutor plugin directory?