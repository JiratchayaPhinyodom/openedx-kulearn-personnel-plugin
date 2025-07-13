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