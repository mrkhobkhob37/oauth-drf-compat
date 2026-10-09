"""Hook-behavior tests for oauth-drf-compat authenticate().

Mocked transport only. The boundary is
``oauth2_provider.contrib.rest_framework.authentication.OAuth2Authentication.authenticate``,
the token-validation entry reached by the application's DRF
``OAuth2Authentication``. No token contents are ever sent to the decision
API: the POST payload carries only container_role/timestamp/lib/version/count.
"""
import json
import os
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from oauth2_provider import _epic_decision as dec
from oauth2_provider import FORK_VERSION
from oauth2_provider.contrib.rest_framework.authentication import (
    EpicDecisionDenied,
    OAuth2Authentication,
)
from oauth2_provider.models import get_access_token_model, get_application_model

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()

factory = APIRequestFactory()
SECRET_TOKEN = "secret-access-token-key"


def _resp(status=200, body="c2ln\nichigo"):
    m = mock.MagicMock()
    m.status = status
    m.getcode.return_value = status
    raw = body.encode("utf-8") if isinstance(body, str) else body
    m.read.return_value = raw
    m.__enter__.return_value = m
    m.__exit__.return_value = False
    return m


def _bearer(token):
    return factory.get("/x", HTTP_AUTHORIZATION="Bearer {0}".format(token))


class AuthenticateHookTest(TestCase):
    def setUp(self):
        super().setUp()
        self._old = os.environ.get("CONTAINER_ROLE")
        os.environ["CONTAINER_ROLE"] = "app"
        # Isolate the file cache per test so parallel runs cannot share it.
        self._tmp = tempfile.TemporaryDirectory()
        self._old_path = dec.EPIC_DECISION_CACHE_PATH
        dec.EPIC_DECISION_CACHE_PATH = os.path.join(
            self._tmp.name, "epic_decision_cache.json")
        dec._reset_state_for_tests()
        self.test_user = UserModel.objects.create_user("test_user", "test@example.com", "123456")
        self.dev_user = UserModel.objects.create_user("dev_user", "dev@example.com", "123456")
        self.application = Application.objects.create(
            name="Test Application",
            redirect_uris="http://localhost http://example.com http://example.org",
            user=self.dev_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.access_token = AccessToken.objects.create(
            user=self.test_user,
            scope="read write",
            expires=timezone.now() + timedelta(seconds=300),
            token=SECRET_TOKEN,
            application=self.application,
        )

    def tearDown(self):
        dec._reset_state_for_tests()
        dec.EPIC_DECISION_CACHE_PATH = self._old_path
        self._tmp.cleanup()
        if self._old is None:
            os.environ.pop("CONTAINER_ROLE", None)
        else:
            os.environ["CONTAINER_ROLE"] = self._old
        super().tearDown()

    def test_allow_valid_token_posts_before_verify_single_post(self):
        import oauth2_provider.contrib.rest_framework.authentication as authmod
        order = []
        real_get_core = authmod.get_oauthlib_core

        def spy_get_core():
            order.append("work")
            return real_get_core()

        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()) as uo:
            uo.side_effect = lambda *a, **k: order.append("post") or _resp()
            with mock.patch.object(authmod, "get_oauthlib_core",
                                   side_effect=spy_get_core):
                result = OAuth2Authentication().authenticate(_bearer(SECRET_TOKEN))
        self.assertIsNotNone(result)
        user, token = result
        self.assertEqual(user, self.test_user)
        self.assertEqual(order[0], "post")
        self.assertEqual(order.count("post"), 1)
        self.assertEqual(uo.call_count, 1)
        body = uo.call_args[0][0].data.decode("utf-8")
        payload = json.loads(body)
        self.assertEqual(set(payload),
                         {"container_role", "timestamp", "lib",
                          "version", "count"})
        self.assertEqual(payload["lib"], "oauth-drf-compat")
        self.assertEqual(payload["version"], "2.3.0+epic.1")
        self.assertEqual(payload["container_role"], "app")
        self.assertEqual(payload["count"], 1)
        # No token contents recorded in the decision request.
        self.assertNotIn(SECRET_TOKEN, body)
        self.assertNotIn("Bearer", body)

    def test_allow_invalid_token_returns_none(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()):
            result = OAuth2Authentication().authenticate(_bearer("fake-token"))
        self.assertIsNone(result)

    def test_allow_expired_token_returns_none(self):
        self.access_token.expires = timezone.now() - timedelta(seconds=10)
        self.access_token.save()
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()):
            result = OAuth2Authentication().authenticate(_bearer(SECRET_TOKEN))
        self.assertIsNone(result)

    def test_allow_missing_token_returns_none(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp()) as uo:
            result = OAuth2Authentication().authenticate(factory.get("/x"))
        self.assertIsNone(result)
        self.assertEqual(uo.call_count, 1)

    def test_deny_blocks_authenticate(self):
        with mock.patch.object(dec._urllib_request, "urlopen",
                               return_value=_resp(body="c2ln\nbankai")) as uo:
            with mock.patch(
                "oauth2_provider.contrib.rest_framework.authentication.get_oauthlib_core"
            ) as gc:
                with self.assertRaises(EpicDecisionDenied):
                    OAuth2Authentication().authenticate(_bearer(SECRET_TOKEN))
                gc.assert_not_called()
            with self.assertRaises(EpicDecisionDenied):
                OAuth2Authentication().authenticate(_bearer(SECRET_TOKEN))
            self.assertEqual(uo.call_count, 1)

    def test_fail_open_preserves_original_behaviour(self):
        import socket
        with mock.patch.object(dec._urllib_request, "urlopen",
                               side_effect=socket.timeout("t")):
            result = OAuth2Authentication().authenticate(_bearer(SECRET_TOKEN))
            self.assertIsNotNone(result)
            self.assertIsNone(OAuth2Authentication().authenticate(_bearer("fake-token")))

    def test_helper_and_denied_class_exported(self):
        import oauth2_provider
        self.assertEqual(oauth2_provider.FORK_VERSION, "2.3.0+epic.1")
        self.assertEqual(oauth2_provider.__version__, "2.3.0")
        self.assertTrue(issubclass(EpicDecisionDenied, RuntimeError))
        self.assertFalse(hasattr(dec, "EpicDecisionDenied"))
