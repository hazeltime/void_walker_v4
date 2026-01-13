import sys
import json
import os
sys.path.insert(0, '.')

# Test type normalization
test_config = 'test_type_normalization_config.json'

print('[Test 1] Integer values in JSON (edge case)')
config_data = {
    'path': 'C:\\temp',
    'mode': 2,
    'disk': 3,
    'strategy': 2,
    'workers': 4
}
with open(test_config, 'w') as f:
    json.dump(config_data, f)

print(f'  Created config with integers: mode={type(config_data["mode"]).__name__}')

from ui.menu import Menu
menu = Menu()
menu.config_file = test_config
loaded = menu.load_config()

print(f'  Loaded mode="{loaded["mode"]}" (type: {type(loaded["mode"]).__name__})')
print(f'  Loaded disk="{loaded["disk"]}" (type: {type(loaded["disk"]).__name__})')
print(f'  Loaded strategy="{loaded["strategy"]}" (type: {type(loaded["strategy"]).__name__})')

assert isinstance(loaded['mode'], str) and loaded['mode'] == '2'
assert isinstance(loaded['disk'], str) and loaded['disk'] == '3'
assert isinstance(loaded['strategy'], str) and loaded['strategy'] == '2'
print('  [OK] All integer values normalized to strings')

os.remove(test_config)
print()
print('[SUCCESS] Bug #4 fix validated - type normalization works')
