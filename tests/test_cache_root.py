import unittest
from pathlib import Path
from unittest.mock import patch

from glm53_setup import config, launch_assets, server


class CacheRootTests(unittest.TestCase):
    def test_hf_home_names_the_cache_the_launcher_mounts(self):
        with patch.dict("os.environ", {"HF_HOME": "/srv/hf-home"}):
            self.assertEqual(config.cache_root(), Path("/srv/hf-home"))

    def test_the_default_is_the_documented_one(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(
                config.cache_root(), Path.home() / ".cache/huggingface"
            )

    def test_hub_cache_alone_does_not_move_the_root(self):
        # HF_HUB_CACHE names hub/ and says nothing about where the MTP view is,
        # so a launcher that composes both under one root cannot honour it.
        with patch.dict("os.environ", {"HF_HUB_CACHE": "/srv/hub"}, clear=True):
            self.assertEqual(
                config.cache_root(), Path.home() / ".cache/huggingface"
            )

    def test_preflight_and_launch_read_the_same_root(self):
        # The regression this guards: preflight derived the snapshot it expects
        # from the home cache while the download state pointed at HF_HOME, and
        # every start failed on a mismatch that named neither path.
        for module in (server, launch_assets):
            self.assertIs(module.cache_root, config.cache_root)


if __name__ == "__main__":
    unittest.main()
