import json
from pathlib import Path


class SaveSystem:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        self.save_dir = base_dir / 'saves'
        self.save_path = self.save_dir / 'savegame.json'

    def has_save(self):
        if not self.save_path.is_file():
            return False
        try:
            data = self.load()
        except (OSError, ValueError):
            return False
        required_keys = {'map', 'player', 'weapon', 'objects'}
        return isinstance(data, dict) and required_keys.issubset(data)

    def save(self, payload):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        with self.save_path.open('w', encoding='utf-8') as save_file:
            json.dump(payload, save_file, ensure_ascii=True, indent=2)
        return str(self.save_path)

    def load(self):
        if not self.save_path.is_file():
            return None
        with self.save_path.open('r', encoding='utf-8') as save_file:
            return json.load(save_file)
