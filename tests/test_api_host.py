import unittest
from pathlib import Path

from glm53_setup import host
from glm53_setup import server_config as config

ROOT = Path(__file__).resolve().parents[1]


class ApiHostTests(unittest.TestCase):
    def setUp(self):
        self.profile = config.load(ROOT / "examples/server.example.toml")

    def bind(self, profile):
        args = host.serve_args(config.site(profile, 0), Path("/hf/model"))
        return args[args.index("--host") + 1]

    def test_the_default_stays_loopback(self):
        self.profile["api"].pop("host", None)
        self.assertEqual(self.bind(self.profile), "127.0.0.1")

    def test_a_profile_may_publish_the_api_on_a_trusted_link(self):
        self.profile["api"]["host"] = "0.0.0.0"
        config.validate(self.profile)
        self.assertEqual(self.bind(self.profile), "0.0.0.0")

    def test_a_bind_address_that_is_not_an_address_is_refused(self):
        for value in ("localhost", "10.0.0.1/24", 8888):
            self.profile["api"]["host"] = value
            with self.assertRaises(ValueError):
                config.validate(self.profile)


if __name__ == "__main__":
    unittest.main()
