import unittest
from src.domain.registry import KINDLE_MODELS
from src.domain.types import TargetHardwareConstraints


class TestDomainRegistry(unittest.TestCase):
    def test_registry_contains_expected_models(self):
        expected_models = [
            "Oasis",
            "Paperwhite",
            "Paperwhite_Signature_Edition",
            "Scribe",
            "Voyage",
            "Kindle_11th_Gen",
            "Basic",
        ]
        for model in expected_models:
            self.assertIn(model, KINDLE_MODELS)
            self.assertIsInstance(KINDLE_MODELS[model], TargetHardwareConstraints)

    def test_constraints_values_are_valid(self):
        for model, constraints in KINDLE_MODELS.items():
            self.assertGreater(
                constraints.width, 0, f"Width for {model} should be positive"
            )
            self.assertGreater(
                constraints.height, 0, f"Height for {model} should be positive"
            )
            self.assertEqual(constraints.dpi, 300, f"DPI for {model} should be 300")

            # margin_crop should be a valid float string
            try:
                margin = float(constraints.margin_crop)
                self.assertGreaterEqual(margin, 0.0)
                self.assertLessEqual(margin, 1.0)
            except ValueError:
                self.fail(
                    f"margin_crop '{constraints.margin_crop}' for {model} is not a valid float"
                )


if __name__ == "__main__":
    unittest.main()
