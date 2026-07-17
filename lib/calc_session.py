import json
import os


DATA_DIR = '/.data'
HISTORY_FILE = DATA_DIR + '/calc_history.txt'
MEMORY_FILE = DATA_DIR + '/calc_memory.txt'


def _ensure_dir():
    try:
        os.stat(DATA_DIR)
    except OSError:
        try:
            os.mkdir(DATA_DIR)
        except:
            pass


def save_history(history):
    _ensure_dir()
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history[-50:], f)
    except:
        pass


def load_history():
    _ensure_dir()
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_memory(memory):
    _ensure_dir()
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f)
    except:
        pass


def load_memory():
    _ensure_dir()
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            defaults = {
                'Ans': 0.0,
                'A': 0.0, 'B': 0.0, 'C': 0.0,
                'D': 0.0, 'E': 0.0, 'F': 0.0,
                'X': 0.0, 'Y': 0.0, 'M': 0.0,
            }
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            return data
    except:
        return {
            'Ans': 0.0,
            'A': 0.0, 'B': 0.0, 'C': 0.0,
            'D': 0.0, 'E': 0.0, 'F': 0.0,
            'X': 0.0, 'Y': 0.0, 'M': 0.0,
        }
