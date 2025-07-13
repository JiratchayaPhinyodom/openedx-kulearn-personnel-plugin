from django.core.management.base import BaseCommand
from ku_personnel_task import approve_course_creators

class Command(BaseCommand):
    help = 'Approve or deny course creator requests'

    def handle(self, *args, **kwargs):
        approve_course_creators.delay()
