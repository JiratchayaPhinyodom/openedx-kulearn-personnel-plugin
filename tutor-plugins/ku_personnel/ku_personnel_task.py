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