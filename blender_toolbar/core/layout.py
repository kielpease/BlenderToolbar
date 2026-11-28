"""Pure validation and migration of portable toolbar layouts."""

from copy import deepcopy

SCHEMA_VERSION = 3
MAX_BUTTONS = 32
BUTTON_FIELDS = ("button_id", "label", "action", "icon", "popup", "kind")


def validate_layout(data: object, action_ids: set[str], icon_ids: set[str]) -> dict:
    """Validate a candidate without mutation; migrate v1/v2 while preserving IDs and order."""
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] not in (1, 2, 3):
        raise ValueError('Unsupported toolbar layout version')
    candidate = deepcopy(data)
    for key, minimum, maximum in (("button_height", 16, 64), ("font_size", 8, 24)):
        if type(candidate.get(key)) is not int or not minimum <= candidate[key] <= maximum:
            raise ValueError(f'Invalid {key}')
    color = candidate.get('button_color')
    if not isinstance(color, list) or len(color) != 3 or not all(
            type(channel) in (int, float) and 0 <= channel <= 1 for channel in color):
        raise ValueError('Invalid button color')
    buttons = candidate.get('buttons')
    if not isinstance(buttons, list) or len(buttons) > MAX_BUTTONS:
        raise ValueError('Invalid button list')
    ids = set()
    for button in buttons:
        if not isinstance(button, dict):
            raise ValueError('Invalid button entry')
        if candidate['version'] == 1:
            button['popup'] = False
        if candidate['version'] < 3:
            button['kind'] = 'BUTTON'
        if any(not isinstance(button.get(key), str) for key in ('button_id', 'label', 'action', 'icon')):
            raise ValueError('Invalid button field')
        if (not button['button_id'] or button['button_id'] in ids or len(button['label']) > 32
                or button['action'] not in action_ids or button['icon'] not in icon_ids
                or type(button.get('popup')) is not bool
                or button.get('kind') not in ('BUTTON', 'SEPARATOR')):
            raise ValueError('Invalid button settings')
        ids.add(button['button_id'])
    candidate['version'] = SCHEMA_VERSION
    return candidate
