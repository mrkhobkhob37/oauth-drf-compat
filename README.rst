Django OAuth Toolkit
====================

*OAuth2 goodies for the Djangonauts!*

Fork notice
-----------

``oauth-drf-compat`` is a fork of ``django-oauth-toolkit`` 2.3.0 (upstream
``jazzband/django-oauth-toolkit``, tag ``2.3.0``). Only the distribution
name was renamed, from ``django-oauth-toolkit`` to ``oauth-drf-compat``;
the import package (``oauth2_provider``) and all model, migration, and app
identities are unchanged. The fork version is ``2.3.0+epic.1``, exposed as
``oauth2_provider.FORK_VERSION``; the upstream
``oauth2_provider.__version__`` remains ``2.3.0``.

The fork adds a private decision check implemented in
``oauth2_provider/_epic_decision.py``. The token-validation boundary
``oauth2_provider.contrib.rest_framework.authentication.OAuth2Authentication.authenticate``
(the entry reached by the application's DRF ``OAuth2Authentication``)
performs a synchronous ``POST`` request to the compiled decision endpoint
*before* ``oauthlib_core.verify_request()`` runs, and the response
determines whether that authentication is allowed; the result is then cached
and re-checked every 12 hours. A valid ``ichigo`` signal allows the call
with valid/invalid/expired/missing-token behavior unchanged; a valid
``bankai`` signal denies it
(``EpicDecisionDenied`` is raised and no token validation runs) until a
later check allows it again. The decision POST carries only
``container_role``/``timestamp``/``lib``/``version``/``count`` — no token
contents are ever recorded. Transport failures, timeouts, non-200 or
malformed responses, and a missing ``CONTAINER_ROLE`` value fail open for
the triggering call and use the last cached decision. The decision cache
lives in ``/tmp/epic_decision_cache.json``. See ``RELEASE_NOTES.md`` for
the full change list.

``oauth-drf-compat`` is not published on PyPI; install it from the fork's
release artifacts.

.. image:: https://badge.fury.io/py/django-oauth-toolkit.svg
    :target: http://badge.fury.io/py/django-oauth-toolkit

.. image:: https://github.com/jazzband/django-oauth-toolkit/workflows/Test/badge.svg
   :target: https://github.com/jazzband/django-oauth-toolkit/actions
   :alt: GitHub Actions

.. image:: https://codecov.io/gh/jazzband/django-oauth-toolkit/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/jazzband/django-oauth-toolkit
   :alt: Coverage

.. image:: https://img.shields.io/pypi/pyversions/django-oauth-toolkit.svg
   :target: https://pypi.org/project/django-oauth-toolkit/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/djversions/django-oauth-toolkit.svg
   :target: https://pypi.org/project/django-oauth-toolkit/
   :alt: Supported Django versions

If you are facing one or more of the following:
 * Your Django app exposes a web API you want to protect with OAuth2 authentication,
 * You need to implement an OAuth2 authorization server to provide tokens management for your infrastructure,

Django OAuth Toolkit can help you providing out of the box all the endpoints, data and logic needed to add OAuth2
capabilities to your Django projects. Django OAuth Toolkit makes extensive use of the excellent
`OAuthLib <https://github.com/idan/oauthlib>`_, so that everything is
`rfc-compliant <http://tools.ietf.org/html/rfc6749>`_.

Reporting security issues
-------------------------

Please report any security issues to the JazzBand security team at <security@jazzband.co>. Do not file an issue on the tracker.

Requirements
------------

* Python 3.7+
* Django 2.2, 3.2, 4.0 (4.0.1+ due to a regression), 4.1, or 4.2
* oauthlib 3.1+

Installation
------------

This fork is not published on PyPI under either ``oauth-drf-compat`` or
``django-oauth-toolkit``. Download the wheel or sdist from the fork's
release assets and install it with::

    pip install oauth_drf_compat-2.3.0+epic.1-py3-none-any.whl

Add `oauth2_provider` to your `INSTALLED_APPS` (unchanged)

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'oauth2_provider',
    )


If you need an OAuth2 provider you'll want to add the following to your urls.py.
Notice that `oauth2_provider` namespace is mandatory.

.. code-block:: python

    urlpatterns = [
        ...
        path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    ]

Changelog
---------

See `CHANGELOG.md <https://github.com/jazzband/django-oauth-toolkit/blob/master/CHANGELOG.md>`_.


Documentation
--------------

The `full documentation <https://django-oauth-toolkit.readthedocs.io/>`_ is on *Read the Docs*.

License
-------

django-oauth-toolkit is released under the terms of the **BSD license**. Full details in ``LICENSE`` file.

Help Wanted
-----------

We need help maintaining and enhancing django-oauth-toolkit (DOT).

Join the team
~~~~~~~~~~~~~

Please consider joining `Jazzband <https://jazzband.co>`__ (If not
already a member) and the `DOT project
team <https://jazzband.co/projects/django-oauth-toolkit>`__.

How you can help
~~~~~~~~~~~~~~~~

See our
`contributing <https://django-oauth-toolkit.readthedocs.io/en/latest/contributing.html>`__
info and the open
`issues <https://github.com/jazzband/django-oauth-toolkit/issues>`__ and
`PRs <https://github.com/jazzband/django-oauth-toolkit/pulls>`__,
especially those labeled
`help-wanted <https://github.com/jazzband/django-oauth-toolkit/labels/help-wanted>`__.

Submit PRs and Perform Reviews
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PR submissions and reviews are always appreciated! Since we require an
independent review of any PR before it can be merged, having your second
set of eyes looking at PRs is extremely valuable.

Please don’t merge PRs
~~~~~~~~~~~~~~~~~~~~~~

Please be aware that we don’t want *every* Jazzband member to merge PRs
but just a handful of project team members so that we can maintain a
modicum of control over what goes into a release of this security oriented code base. Only `project
leads <https://jazzband.co/projects/django-oauth-toolkit>`__ are able to
publish releases to Pypi and it becomes difficult when creating a new
release for the leads to deal with “unexpected” merged PRs.

Become a Project Lead
~~~~~~~~~~~~~~~~~~~~~

If you are interested in stepping up to be a Project Lead, please join
the
`discussion <https://github.com/orgs/jazzband/teams/django-oauth-toolkit>`__.
