"""Regression tests for portable layout migration and failure preservation."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from blender_toolbar.core.layout import validate_layout
from blender_toolbar.storage.layout import read_layout, write_layout

ACTIONS = {'ADD_CUBE', 'ADD_SPLINE', 'MATERIALS'}
ICONS = {'AUTO'}


def sample():
    return {'version': 1, 'button_height': 24, 'font_size': 11,
            'button_color': [0.2, 0.2, 0.2], 'buttons': [
                {'button_id': 'stable-id', 'label': '', 'action': 'ADD_SPLINE', 'icon': 'AUTO'}]}


class LayoutTests(unittest.TestCase):
    def test_migration_preserves_identity_and_does_not_mutate_input(self):
        original = sample()
        snapshot = deepcopy(original)
        migrated = validate_layout(original, ACTIONS, ICONS)
        self.assertEqual(original, snapshot)
        self.assertEqual(migrated['version'], 3)
        self.assertEqual(migrated['buttons'][0]['button_id'], 'stable-id')
        self.assertIs(migrated['buttons'][0]['popup'], False)

    def test_future_version_duplicate_ids_and_non_boolean_popup_are_rejected(self):
        cases = []
        future = sample()
        future['version'] = 99
        cases.append(future)
        duplicate = sample()
        duplicate['buttons'].append(deepcopy(duplicate['buttons'][0]))
        cases.append(duplicate)
        invalid_popup = validate_layout(sample(), ACTIONS, ICONS)
        invalid_popup['buttons'][0]['popup'] = 1
        cases.append(invalid_popup)
        for candidate in cases:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                validate_layout(candidate, ACTIONS, ICONS)

    def test_v2_migration_and_separator_roundtrip_preserve_order(self):
        candidate = sample()
        candidate['version'] = 2
        candidate['buttons'][0]['popup'] = True
        candidate = validate_layout(candidate, ACTIONS, ICONS)
        self.assertEqual(candidate['buttons'][0]['kind'], 'BUTTON')
        self.assertTrue(candidate['buttons'][0]['popup'])
        separator = deepcopy(candidate['buttons'][0])
        separator.update(button_id='separator-id', label='Modeling', kind='SEPARATOR')
        candidate['buttons'].insert(0, separator)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'layout.json'
            write_layout(path, candidate, ACTIONS, ICONS)
            self.assertEqual(read_layout(path, ACTIONS, ICONS), candidate)
        invalid = deepcopy(candidate)
        invalid['buttons'][0]['kind'] = 'SCRIPT'
        with self.assertRaises(ValueError):
            validate_layout(invalid, ACTIONS, ICONS)

    def test_popup_roundtrip(self):
        candidate = validate_layout(sample(), ACTIONS, ICONS)
        candidate['buttons'][0]['popup'] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'layout.json'
            write_layout(path, candidate, ACTIONS, ICONS)
            self.assertEqual(read_layout(path, ACTIONS, ICONS), candidate)

    def test_invalid_candidate_and_failed_replace_preserve_previous_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'layout.json'
            write_layout(path, sample(), ACTIONS, ICONS)
            previous = path.read_bytes()
            invalid = sample()
            invalid['buttons'][0]['action'] = 'UNKNOWN'
            with self.assertRaises(ValueError):
                write_layout(path, invalid, ACTIONS, ICONS)
            self.assertEqual(path.read_bytes(), previous)
            with patch('blender_toolbar.storage.layout.os.replace', side_effect=OSError('disk failure')):
                with self.assertRaises(OSError):
                    write_layout(path, sample(), ACTIONS, ICONS)
            self.assertEqual(path.read_bytes(), previous)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == '__main__':
    unittest.main()
