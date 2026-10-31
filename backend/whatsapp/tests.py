import os
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from reports.models import Report
from risk.engine import score_area
from risk.models import Area
from .bot import handle_message


class BotAndRiskTests(TestCase):
    def setUp(self):
        call_command("seed_areas", verbosity=0)
        patcher = mock.patch.dict(os.environ, {"DEMO_RAIN_MM": "50"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_subscribe_flow(self):
        self.assertIn("Which area", handle_message("260971", "hi"))
        names = list(Area.objects.order_by("name").values_list("name", flat=True))
        reply = handle_message("260971", "1")
        self.assertIn(names[0], reply)
        self.assertIn("Flood risk", reply)

    def test_reports_raise_flood_risk(self):
        matero = Area.objects.get(name="Matero")  # not flood-prone
        with mock.patch.dict(os.environ, {"DEMO_RAIN_MM": "25"}):
            self.assertEqual(score_area(matero)["flood"], "MEDIUM")
            for _ in range(2):
                Report.objects.create(kind="flooding", area="Matero", submitter_phone_hash="x")
            self.assertEqual(score_area(matero)["flood"], "HIGH")
            Report.objects.all().update(review_status="rejected")
            self.assertEqual(score_area(matero)["flood"], "MEDIUM")

    def test_flood_prone_bumps_level(self):
        self.assertEqual(score_area(Area.objects.get(name="Kanyama"))["flood"], "HIGH")

    def test_water_risk_from_reports(self):
        a = Area.objects.get(name="Matero")
        self.assertEqual(score_area(a)["water"], "LOW")
        for _ in range(3):
            Report.objects.create(kind="dry_tap", area="Matero", submitter_phone_hash="x")
        self.assertEqual(score_area(a)["water"], "HIGH")

    def test_low_rain_is_low(self):
        with mock.patch.dict(os.environ, {"DEMO_RAIN_MM": "2"}):
            self.assertEqual(score_area(Area.objects.get(name="Kanyama"))["flood"], "LOW")

    def test_report_via_bot_and_stop_deletes(self):
        handle_message("p1", "hi")
        handle_message("p1", "1")
        handle_message("p1", "2")
        self.assertEqual(Report.objects.filter(kind="flooding").count(), 1)
        handle_message("p1", "stop")
        self.assertEqual(Report.objects.filter(submitter_phone_hash="deleted").count(), 1)

    def test_endpoints(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        j = self.client.get("/api/map/").json()
        self.assertEqual(len(j["areas"]), 5)
        r = self.client.post("/api/reports/", {"kind": "flooding", "area": "Kanyama"}, content_type="application/json")
        self.assertEqual(r.status_code, 201)
        r = self.client.post("/demo/message/", {"phone": "1", "text": "hi"}, content_type="application/json")
        self.assertIn("reply", r.json())
        self.assertEqual(self.client.get("/webhook/whatsapp/?hub.mode=subscribe&hub.verify_token=x").status_code, 403)
