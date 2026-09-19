import unittest
from pathlib import Path

from glm53_setup import server
from glm53_setup import server_config as config

ROOT = Path(__file__).resolve().parents[1]
OTHER = "sha256:" + "3f" * 32


class NodeImageTests(unittest.TestCase):
    def setUp(self):
        self.profile = config.load(ROOT / "examples/server.example.toml")
        self.profile["lpa"]["enabled"] = False

    def test_without_an_override_every_rank_uses_the_profile_image(self):
        for rank in (0, 1):
            self.assertEqual(
                config.selected_image(self.profile, rank),
                self.profile["runtime"]["reference_image"],
            )

    def test_a_node_may_name_the_id_its_own_daemon_reports(self):
        # The same image, saved from a classic image store and loaded into a
        # containerd one, arrives under a different config digest.
        self.profile["nodes"][1]["reference_image"] = OTHER
        config.validate(self.profile)
        self.assertEqual(config.selected_image(self.profile, 0),
                         self.profile["runtime"]["reference_image"])
        self.assertEqual(config.selected_image(self.profile, 1), OTHER)

    def test_the_override_follows_the_lpa_selection(self):
        self.profile["nodes"][1]["reference_image"] = OTHER
        self.profile["lpa"]["enabled"] = True
        self.assertEqual(config.selected_image(self.profile, 1),
                         self.profile["runtime"]["lpa_image"])

    def test_an_override_that_is_not_an_image_id_is_refused(self):
        for value in ("glm53-enterprise:reference", "sha256:0", 7):
            self.profile["nodes"][0]["reference_image"] = value
            with self.assertRaises(ValueError):
                config.validate(self.profile)

    def test_the_container_command_carries_the_local_id(self):
        self.profile["nodes"][1]["reference_image"] = OTHER
        args = server.command(self.profile, ROOT / "examples/server.example.toml", 1,
                              "glm53-enterprise-rank1")
        self.assertIn(OTHER, args)


if __name__ == "__main__":
    unittest.main()
