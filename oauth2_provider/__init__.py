import django


__version__ = "2.3.0"
# Fork version: upstream __version__ above is preserved; the fork
# distribution version is frozen explicitly here and in setup.cfg.
FORK_VERSION = "2.3.0+epic.1"

if django.VERSION < (3, 2):
    default_app_config = "oauth2_provider.apps.DOTConfig"
