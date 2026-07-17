def note_to_freq(note):
    if not note or note == 'R':
        return 0
    notes = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}
    name = note[0]
    if len(note) > 2 and note[1] == '#':
        semitone = notes[name] + 1
        octave = int(note[2])
    elif len(note) > 1 and note[1].isdigit():
        semitone = notes[name]
        octave = int(note[1])
    else:
        return 0
    return int(440 * 2 ** ((semitone - 9 + (octave - 4) * 12) / 12))


WAV_SONGS = {
    'DOOM OST': '/sd/music/songs/doom.wav',
    'Assumptions': '/sd/music/songs/assumptions.wav',
    'Slash Inferno': '/sd/music/songs/slash_inferno.wav',
    'SCF Instrumental': '/sd/music/songs/scf.wav',
    'RUSH E': '/sd/music/songs/rush_e.wav',
    'Emptiness': '/sd/music/songs/emptiness.wav',
    'Imposter Syndrome': '/sd/music/songs/imposter.wav',
    'Sweet Dreams': '/sd/music/songs/sweet_dreams.wav',
    'Du bist gut genug': '/sd/music/songs/dubist.wav',
}

WAV_NAMES = list(WAV_SONGS.keys())
