import random

ITEMS = {
    'sword': {'desc': 'A sharp steel blade', 'attack': 5, 'type': 'weapon'},
    'shield': {'desc': 'A sturdy wooden shield', 'defense': 3, 'type': 'armor'},
    'potion': {'desc': 'A glowing red potion', 'heal': 20, 'type': 'consumable'},
    'key': {'desc': 'An ornate brass key', 'type': 'key'},
    'torch': {'desc': 'A burning torch', 'type': 'light'},
    'gold coins': {'desc': 'Shiny gold coins', 'gold': 10, 'type': 'currency'},
    'magic amulet': {'desc': 'A glowing amulet (+3 atk)', 'attack': 3, 'type': 'accessory'},
    'health crystal': {'desc': 'A pulsing crystal (heal 30)', 'heal': 30, 'type': 'consumable'},
    'dragon scale': {'desc': 'Scale from a defeated dragon', 'type': 'trophy'},
}

ENEMIES = {
    'rat': {'name': 'Giant Rat', 'hp': 10, 'max_hp': 10, 'attack': 2, 'defense': 0, 'reward': 5, 'xp': 3},
    'goblin': {'name': 'Goblin Warrior', 'hp': 20, 'max_hp': 20, 'attack': 5, 'defense': 1, 'reward': 15, 'xp': 8},
    'skeleton': {'name': 'Skeleton Knight', 'hp': 30, 'max_hp': 30, 'attack': 8, 'defense': 2, 'reward': 25, 'xp': 15},
    'dragon': {'name': 'Ancient Dragon', 'hp': 50, 'max_hp': 50, 'attack': 12, 'defense': 4, 'reward': 100, 'xp': 50},
    'bat': {'name': 'Vampire Bat', 'hp': 8, 'max_hp': 8, 'attack': 3, 'defense': 0, 'reward': 4, 'xp': 2},
    'spider': {'name': 'Giant Spider', 'hp': 12, 'max_hp': 12, 'attack': 4, 'defense': 0, 'reward': 7, 'xp': 5},
}

ROOMS = {
    'entrance': {
        'name': 'Dungeon Entrance',
        'desc': 'A massive stone archway looms above.\nCobwebs cling to the crumbling walls.\nFresh air drifts from behind you.',
        'exits': {'north': 'hallway'},
        'items': ['torch'],
        'enemy': None,
        'visited': False,
        'dark': False,
    },
    'hallway': {
        'name': 'Grand Hallway',
        'desc': 'A long corridor with flickering torches.\nCracked tiles line the floor.\nPassages branch east and south.',
        'exits': {'south': 'entrance', 'east': 'armory', 'west': 'kitchen'},
        'items': [],
        'enemy': {'template': 'rat'},
        'visited': False,
        'dark': False,
    },
    'armory': {
        'name': 'Ancient Armory',
        'desc': 'Rusty weapons line the walls.\nA sturdy sword rests on a stone pedestal.\nA shield hangs from the wall.',
        'exits': {'west': 'hallway', 'north': 'library'},
        'items': ['sword', 'shield'],
        'enemy': None,
        'visited': False,
        'dark': False,
    },
    'library': {
        'name': 'Dusty Library',
        'desc': 'Shelves of ancient books fill the room.\nA strange map is drawn on the wall.\nThe air smells of old parchment.',
        'exits': {'south': 'armory'},
        'items': ['magic amulet'],
        'enemy': {'template': 'spider'},
        'visited': False,
        'dark': False,
    },
    'kitchen': {
        'name': 'Abandoned Kitchen',
        'desc': 'Broken pots and pans litter the floor.\nA barrel of water sits in the corner.\nSomething skitters in the shadows.',
        'exits': {'east': 'hallway', 'south': 'cellar'},
        'items': ['potion', 'potion'],
        'enemy': {'template': 'rat'},
        'visited': False,
        'dark': False,
    },
    'cellar': {
        'name': 'Dark Cellar',
        'desc': 'Stairs descend into darkness.\nThe smell of damp earth fills your nose.\nPassages lead east and south.',
        'exits': {'north': 'kitchen', 'east': 'tunnel', 'south': 'dungeon'},
        'items': ['gold coins'],
        'enemy': {'template': 'bat'},
        'visited': False,
        'dark': True,
    },
    'tunnel': {
        'name': 'Narrow Tunnel',
        'desc': 'A tight passage carved through rock.\nWater drips from the ceiling.\nThe tunnel leads to a grand door.',
        'exits': {'west': 'cellar', 'north': 'treasury'},
        'items': ['health crystal'],
        'enemy': None,
        'visited': False,
        'dark': False,
    },
    'dungeon': {
        'name': 'Prison Dungeon',
        'desc': 'Iron bars line the walls.\nBones are scattered on the floor.\nA passage leads deeper east.',
        'exits': {'north': 'cellar', 'east': 'crypt'},
        'items': ['key'],
        'enemy': {'template': 'skeleton'},
        'visited': False,
        'dark': True,
    },
    'crypt': {
        'name': 'Ancient Crypt',
        'desc': 'Stone coffins stand in rows.\nGhostly light flickers from within.\nThe air is cold and still.',
        'exits': {'west': 'dungeon', 'north': 'secret_passage'},
        'items': ['gold coins', 'potion'],
        'enemy': {'template': 'skeleton'},
        'visited': False,
        'dark': True,
    },
    'secret_passage': {
        'name': 'Secret Passage',
        'desc': 'A hidden corridor behind the crypt.\nStrange symbols glow on the walls.\nIt curves toward a heavy door.',
        'exits': {'south': 'crypt', 'east': 'treasury'},
        'items': ['magic amulet'],
        'enemy': {'template': 'spider'},
        'visited': False,
        'dark': False,
    },
    'throne_room': {
        'name': 'Throne Room',
        'desc': 'A golden throne sits on a dais.\nCrown jewels sparkle in the light.\nYou have found the heart of the dungeon!',
        'exits': {'west': 'armory'},
        'items': ['gold coins', 'gold coins', 'gold coins'],
        'enemy': None,
        'visited': False,
        'dark': False,
        'locked': True,
        'lock_key': 'key',
    },
    'treasury': {
        'name': 'Dragon Treasury',
        'desc': 'Mountains of gold glitter before you.\nBut a massive dragon guards its hoard.\nThis is the final challenge!',
        'exits': {'south': 'tunnel', 'west': 'secret_passage'},
        'items': ['dragon scale'],
        'enemy': {'template': 'dragon'},
        'visited': False,
        'dark': False,
    },
}

MAP_LAYOUT = (
    '         [armory]---[library]\n'
    '            |\n'
    '[kitchen]--[hallway]\n'
    '    |            \n'
    '[cellar]    [entrance]\n'
    '    |\n'
    '[tunnel]   [dungeon]\n'
    '    |            |\n'
    '[treasury] [crypt]\n'
    '     \\         |\n'
    '  [secret_passage]\n'
    '         |\n'
    '  [throne_room]'
)


def create_game():
    rooms = {}
    for rid, rdata in ROOMS.items():
        rooms[rid] = {
            'name': rdata['name'],
            'desc': rdata['desc'],
            'exits': dict(rdata['exits']),
            'items': list(rdata['items']),
            'enemy': None,
            'visited': False,
            'dark': rdata.get('dark', False),
            'locked': rdata.get('locked', False),
            'lock_key': rdata.get('lock_key', None),
        }
        if rdata.get('enemy'):
            tmpl = rdata['enemy']['template']
            base = ENEMIES[tmpl]
            rooms[rid]['enemy'] = {
                'template': tmpl,
                'name': base['name'],
                'hp': base['hp'],
                'max_hp': base['max_hp'],
                'attack': base['attack'],
                'defense': base['defense'],
                'reward': base['reward'],
                'xp': base['xp'],
                'alive': True,
            }

    return {
        'hp': 50,
        'max_hp': 50,
        'attack': 5,
        'defense': 0,
        'inventory': [],
        'room': 'entrance',
        'gold': 0,
        'weapon': None,
        'armor': None,
        'accessory': None,
        'rooms': rooms,
        'turns': 0,
        'kills': 0,
        'xp': 0,
        'level': 1,
        'in_combat': False,
        'game_over': False,
        'won': False,
        'has_torch': False,
    }


def get_room_description(game):
    room = game['rooms'][game['room']]
    lines = []
    lines.append(f'=== {room["name"]} ===')

    if room['dark'] and not game['has_torch']:
        lines.append('It is too dark to see!')
        lines.append('You need a torch.')
    else:
        lines.append(room['desc'])

    if room['locked']:
        lines.append('The door is locked. You need a key.')

    if room['items']:
        items_here = []
        for item in room['items']:
            if item in ITEMS:
                items_here.append(item)
            else:
                items_here.append(item)
        lines.append(f'Items: {", ".join(items_here)}')

    if room['enemy'] and room['enemy']['alive']:
        e = room['enemy']
        lines.append(f'A {e["name"]} blocks your path! (HP: {e["hp"]}/{e["max_hp"]})')

    exits = list(room['exits'].keys())
    lines.append(f'Exits: {", ".join(exits)}')

    return lines


def get_player_status(game):
    lines = []
    lines.append('=== Status ===')
    lines.append(f'HP: {game["hp"]}/{game["max_hp"]}')
    lines.append(f'ATK: {game["attack"]} DEF: {game["defense"]}')
    lines.append(f'Gold: {game["gold"]}  XP: {game["xp"]}  Lvl: {game["level"]}')
    if game['weapon']:
        lines.append(f'Weapon: {game["weapon"]}')
    if game['armor']:
        lines.append(f'Armor: {game["armor"]}')
    if game['accessory']:
        lines.append(f'Accessory: {game["accessory"]}')
    lines.append(f'Turns: {game["turns"]}  Kills: {game["kills"]}')
    return lines


def get_inventory_display(game):
    lines = ['=== Inventory ===']
    if not game['inventory']:
        lines.append('  (empty)')
    else:
        counts = {}
        for item in game['inventory']:
            counts[item] = counts.get(item, 0) + 1
        for item, count in sorted(counts.items()):
            info = ITEMS.get(item, {})
            extra = ''
            if 'attack' in info:
                extra = f' +{info["attack"]} atk'
            elif 'defense' in info:
                extra = f' +{info["defense"]} def'
            elif 'heal' in info:
                extra = f' heal {info["heal"]}'
            elif 'gold' in info:
                extra = f' +{info["gold"]} gold'
            lines.append(f'  {item} x{count}{extra}')
    return lines


def process_command(game, command):
    if game['game_over']:
        return ['Game is over. Start a new game!'], game

    cmd = command.strip().lower()
    parts = cmd.split(None, 1)
    action = parts[0] if parts else ''
    target = parts[1] if len(parts) > 1 else ''

    game['turns'] += 1
    lines = []

    if action in ('go', 'move', 'walk'):
        direction = target.split()[0] if target else ''
        lines, game = _move(game, direction)
    elif action in ('north', 'south', 'east', 'west', 'n', 's', 'e', 'w'):
        dir_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        lines, game = _move(game, dir_map.get(action, action))
    elif action in ('take', 'get', 'grab', 'pickup'):
        lines, game = _take(game, target)
    elif action in ('use',):
        lines, game = _use(game, target)
    elif action in ('attack', 'fight', 'hit', 'kill'):
        lines, game = _attack(game)
    elif action in ('flee', 'run', 'escape'):
        lines, game = _flee(game)
    elif action in ('inventory', 'i', 'inv'):
        lines = get_inventory_display(game)
    elif action in ('look', 'l', 'examine'):
        lines = get_room_description(game)
    elif action in ('map', 'm'):
        lines = ['=== Map ==='] + MAP_LAYOUT.split('\n')
    elif action in ('status', 'stats', 'st'):
        lines = get_player_status(game)
    elif action in ('help', 'h', '?'):
        lines = _help_text()
    elif action in ('equip',):
        lines, game = _equip(game, target)
    elif action in ('drop',):
        lines, game = _drop(game, target)
    elif action in ('open',):
        lines, game = _open_door(game)
    elif action in ('quit', 'exit', 'q'):
        lines = ['Thanks for playing!']
        game['game_over'] = True
    else:
        lines.append(f'Unknown command: "{action}"')
        lines.append('Type "help" for commands.')

    return lines, game


def _move(game, direction):
    room = game['rooms'][game['room']]

    if not direction:
        return ['Go where? Specify a direction.'], game

    if room.get('locked') and direction in room['exits']:
        return ['The door is locked! You need a key. Type "open" to use it.'], game

    if direction not in room['exits']:
        valid = list(room['exits'].keys())
        return [f'Cannot go {direction}. Exits: {", ".join(valid)}'], game

    dest_id = room['exits'][direction]
    dest = game['rooms'][dest_id]

    if dest.get('locked') and 'key' not in game['inventory']:
        return ['The door is locked! You need to find a key.'], game

    if dest['enemy'] and dest['enemy']['alive'] and game['in_combat'] is False:
        game['in_combat'] = True

    game['room'] = dest_id
    dest['visited'] = True

    return get_room_description(game), game


def _take(game, item_name):
    room = game['rooms'][game['room']]

    if room['dark'] and not game['has_torch']:
        return ['It is too dark to take anything! Find a torch first.'], game

    if not item_name:
        if room['items']:
            return [f'Items here: {", ".join(room["items"])}. Use "take [item]".'], game
        return ['Nothing to take here.'], game

    if item_name not in room['items']:
        return [f'No "{item_name}" here.'], game

    room['items'].remove(item_name)
    game['inventory'].append(item_name)

    if item_name == 'torch':
        game['has_torch'] = True

    info = ITEMS.get(item_name, {})
    msg = f'Took {item_name}.'
    if 'gold' in info:
        game['gold'] += info['gold']
        msg += f' +{info["gold"]} gold!'
    return [msg], game


def _use(game, item_name):
    if not item_name:
        return ['Use what? Specify an item.'], game

    if item_name == 'torch':
        if 'torch' in game['inventory']:
            game['has_torch'] = True
            return ['You light the torch. The darkness recedes!'], game
        return ['You don\'t have a torch.'], game

    if item_name == 'potion' or item_name == 'health crystal':
        if item_name not in game['inventory']:
            return [f'You don\'t have {item_name}.'], game
        info = ITEMS.get(item_name, {})
        heal = info.get('heal', 20)
        old_hp = game['hp']
        game['hp'] = min(game['max_hp'], game['hp'] + heal)
        healed = game['hp'] - old_hp
        game['inventory'].remove(item_name)
        return [f'Used {item_name}. Healed {healed} HP! (HP: {game["hp"]}/{game["max_hp"]})'], game

    if item_name == 'key':
        if 'key' not in game['inventory']:
            return ['You don\'t have a key.'], game
        room = game['rooms'][game['room']]
        if room.get('locked'):
            room['locked'] = False
            game['inventory'].remove('key')
            return ['You unlock the door with the key!'], game
        # Check if adjacent rooms have locks
        for exit_dir, rid in room['exits'].items():
            dest = game['rooms'][rid]
            if dest.get('locked'):
                dest['locked'] = False
                game['inventory'].remove('key')
                return [f'You unlock the door to the {dest["name"]}!'], game
        return ['No locked door here.'], game

    if item_name == 'sword':
        return ['The sword is already equipped as your weapon. Use "attack" to fight.'], game

    if item_name == 'shield':
        return ['The shield is passive armor. It boosts your defense.'], game

    return [f'Cannot use "{item_name}" directly.'], game


def _equip(game, item_name):
    if not item_name:
        return ['Equip what?'], game

    if item_name not in game['inventory']:
        return [f'You don\'t have {item_name}.'], game

    info = ITEMS.get(item_name, {})
    if info.get('type') == 'weapon':
        if game['weapon']:
            old = game['weapon']
            old_info = ITEMS.get(old, {})
            game['attack'] -= old_info.get('attack', 0)
            game['inventory'].append(old)
        game['weapon'] = item_name
        game['attack'] += info.get('attack', 0)
        game['inventory'].remove(item_name)
        return [f'Equipped {item_name}! ATK is now {game["attack"]}.'], game

    if info.get('type') == 'armor':
        if game['armor']:
            old = game['armor']
            old_info = ITEMS.get(old, {})
            game['defense'] -= old_info.get('defense', 0)
            game['inventory'].append(old)
        game['armor'] = item_name
        game['defense'] += info.get('defense', 0)
        game['inventory'].remove(item_name)
        return [f'Equipped {item_name}! DEF is now {game["defense"]}.'], game

    if info.get('type') == 'accessory':
        if game['accessory']:
            old = game['accessory']
            old_info = ITEMS.get(old, {})
            game['attack'] -= old_info.get('attack', 0)
            game['inventory'].append(old)
        game['accessory'] = item_name
        game['attack'] += info.get('attack', 0)
        game['inventory'].remove(item_name)
        return [f'Equipped {item_name}! ATK is now {game["attack"]}.'], game

    return [f'Cannot equip {item_name}.'], game


def _drop(game, item_name):
    if not item_name:
        return ['Drop what?'], game
    if item_name not in game['inventory']:
        return [f'You don\'t have {item_name}.'], game
    game['inventory'].remove(item_name)
    game['rooms'][game['room']]['items'].append(item_name)
    return [f'Dropped {item_name}.'], game


def _open_door(game):
    room = game['rooms'][game['room']]
    if not room.get('locked'):
        return ['No locked door here.'], game
    if 'key' in game['inventory']:
        room['locked'] = False
        game['inventory'].remove('key')
        return ['You unlock the door with the key!'], game
    return ['The door is locked. You need a key.'], game


def _attack(game):
    room = game['rooms'][game['room']]

    if not room['enemy'] or not room['enemy']['alive']:
        return ['No enemy to attack here.'], game

    if room['dark'] and not game['has_torch']:
        return ['It is too dark to fight! You need a torch.'], game

    enemy = room['enemy']
    lines = []

    player_dmg = max(1, game['attack'] - enemy['defense'])
    enemy['hp'] -= player_dmg
    lines.append(f'You hit {enemy["name"]} for {player_dmg} damage!')

    if enemy['hp'] <= 0:
        enemy['alive'] = False
        game['kills'] += 1
        game['xp'] += enemy['xp']
        game['gold'] += enemy['reward']
        lines.append(f'{enemy["name"]} defeated! +{enemy["reward"]} gold +{enemy["xp"]} xp')
        game['in_combat'] = False
        _check_level_up(game, lines)
        return lines, game

    enemy_dmg = max(1, enemy['attack'] - game['defense'])
    game['hp'] -= enemy_dmg
    lines.append(f'{enemy["name"]} hits you for {enemy_dmg} damage! (HP: {game["hp"]}/{game["max_hp"]})')

    if game['hp'] <= 0:
        game['hp'] = 0
        game['game_over'] = True
        lines.append('You have been slain...')
        lines.append('Game Over! Type "adventure" to restart.')

    return lines, game


def combat_round(game, action):
    return _attack(game) if action == 'attack' else _flee(game)


def _flee(game):
    room = game['rooms'][game['room']]
    if not room['enemy'] or not room['enemy']['alive']:
        return ['Nothing to flee from.'], game

    if random.random() < 0.5:
        exits = list(room['exits'].keys())
        if exits:
            flee_dir = random.choice(exits)
            dest_id = room['exits'][flee_dir]
            game['room'] = dest_id
            game['in_combat'] = False
            lines = [f'You fled {flee_dir}!']
            lines += get_room_description(game)
            return lines, game
    return ['Failed to flee!'], game


def _check_level_up(game, lines):
    xp_needed = game['level'] * 20
    while game['xp'] >= xp_needed:
        game['xp'] -= xp_needed
        game['level'] += 1
        game['max_hp'] += 10
        game['hp'] = min(game['hp'] + 10, game['max_hp'])
        game['attack'] += 2
        lines.append(f'Level Up! Now level {game["level"]}!')
        lines.append(f'HP: {game["max_hp"]} ATK: {game["attack"]}')
        xp_needed = game['level'] * 20


def _help_text():
    return [
        '=== Adventure Commands ===',
        '',
        '  go [dir]       Move (north/south/east/west)',
        '  n/s/e/w        Quick move',
        '  take [item]    Pick up item',
        '  use [item]     Use item (potion, key, torch)',
        '  equip [item]   Equip weapon/armor',
        '  drop [item]    Drop an item',
        '  open           Unlock locked door with key',
        '  attack/fight   Attack enemy',
        '  flee           Run from combat',
        '  inventory (i)  Show inventory',
        '  look (l)       Look around',
        '  status (st)    Show player stats',
        '  map (m)        Show dungeon map',
        '  quit           End game',
        '',
        'Tip: Explore all rooms, find the key,',
        'defeat the dragon, and claim the treasury!',
    ]
