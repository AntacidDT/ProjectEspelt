"""High score persistence for games."""

_HIGHSCORES_FILE = '/sd/highscores.txt'

_cache = {}


def _load():
    global _cache
    if _cache:
        return _cache
    try:
        with open(_HIGHSCORES_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    game, score = line.split(':', 1)
                    try:
                        _cache[game.strip()] = int(score.strip())
                    except:
                        pass
    except:
        pass
    return _cache


def _save():
    try:
        with open(_HIGHSCORES_FILE, 'w') as f:
            for game, score in _cache.items():
                f.write(f'{game}:{score}\n')
        return True
    except:
        return False


def get(game):
    return _load().get(game, 0)


def set(game, score):
    data = _load()
    if score > data.get(game, 0):
        data[game] = score
        _save()
        return True
    return False


def is_new_record(game, score):
    return score > get(game)


def all_scores():
    return dict(_load())


def show():
    data = _load()
    if not data:
        return ['  No high scores yet']
    lines = ['=== High Scores ===']
    for game in sorted(data.keys()):
        lines.append(f'  {game}: {data[game]}')
    return lines
