from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from field_peer import load_scene, probe


class NativeFixtureTests(unittest.TestCase):
    def test_kernel_observation(self):
        with TemporaryDirectory(prefix='obs-') as scratch:
            self.assertIn('观测', probe(load_scene(), Path(scratch)))

    def test_session_actions_are_ordered(self):
        scene = load_scene()
        actions = scene['actions']
        self.assertGreater(len(actions), 5)
        self.assertEqual(sorted(row[0] for row in actions), [row[0] for row in actions])


if __name__ == '__main__':
    unittest.main()
