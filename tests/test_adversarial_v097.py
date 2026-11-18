"""Adversarial tests for the guided dashboard journey in v0.9.7."""
import ast
import unittest
from pathlib import Path

from src.dashboard.demo_journey import (
    DEMO_STEPS, DemoJourneyError, build_demo_journey, get_demo_step,
    validate_demo_navigation,
)

ROOT = Path(__file__).resolve().parents[1]


class DemoJourneyV097(unittest.TestCase):
    def test_journey_has_exactly_six_dashboard_sections(self):
        journey = build_demo_journey()
        self.assertEqual(len(journey["steps"]), 6)
        self.assertEqual(journey["sections"], [x["section"] for x in DEMO_STEPS])

    def test_journey_total_duration_is_fifteen_minutes(self):
        self.assertEqual(build_demo_journey()["total_minutes"], 15)

    def test_every_step_has_purpose_action_message_and_duration(self):
        for step in build_demo_journey()["steps"]:
            with self.subTest(section=step["section"]):
                for key in ("purpose", "action", "message"):
                    self.assertTrue(step[key].strip())
                self.assertGreater(step["duration_minutes"], 0)

    def test_step_lookup_returns_expected_section(self):
        self.assertEqual(get_demo_step("Trazabilidad")["order"], 6)

    def test_unknown_step_is_rejected(self):
        with self.assertRaises(DemoJourneyError):
            get_demo_step("Modelo predictivo conectado")

    def test_empty_step_is_rejected(self):
        with self.assertRaises(DemoJourneyError):
            get_demo_step(" ")

    def test_canonical_navigation_passes(self):
        self.assertTrue(validate_demo_navigation(build_demo_journey()["sections"])["valid"])

    def test_reordered_navigation_fails(self):
        sections = build_demo_journey()["sections"]
        sections[0], sections[1] = sections[1], sections[0]
        self.assertFalse(validate_demo_navigation(sections)["valid"])

    def test_duplicate_navigation_fails(self):
        sections = build_demo_journey()["sections"]
        sections[-1] = sections[0]
        result = validate_demo_navigation(sections)
        self.assertFalse(result["valid"])
        self.assertTrue(result["duplicates"])

    def test_unknown_and_missing_navigation_sections_are_reported(self):
        result = validate_demo_navigation(["Resumen", "Inventada"])
        self.assertFalse(result["valid"])
        self.assertEqual(result["unknown"], ["Inventada"])
        self.assertIn("Trazabilidad", result["missing"])

    def test_navigation_input_type_is_validated(self):
        with self.assertRaises(DemoJourneyError):
            validate_demo_navigation("Resumen")

    def test_synthetic_only_and_disconnected_model_are_explicit(self):
        journey = build_demo_journey()
        self.assertTrue(journey["synthetic_only"])
        self.assertFalse(journey["predictive_model_connected"])

    def test_app_contains_guided_journey_in_sidebar(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn("Guía de recorrido", source)
        self.assertIn("build_demo_journey", source)
        self.assertIn("get_demo_step", source)

    def test_generator_version_is_incremented(self):
        self.assertIn("generator_version'] = 'v1.0.0'", (ROOT / "run_demo.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
