import mido


def load_events(path):
    """Повертає (events, duration).

    events: список нот {track, note, start, duration, velocity}, відсортований за start.
    duration: тривалість файлу в секундах.
    """
    mid = mido.MidiFile(path)
    # темп береться з файлу (доріжка 0 містить set_tempo)
    tempo = next((m.tempo for m in mid.tracks[0] if m.type == 'set_tempo'), 500000)
    events = []
    for ti, track in enumerate(mid.tracks):
        t, open_notes = 0.0, {}
        for msg in track:
            t += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
            if msg.type == 'note_on' and msg.velocity > 0:
                open_notes[msg.note] = (t, msg.velocity)
            elif msg.type in ('note_off', 'note_on') and msg.note in open_notes:
                start, vel = open_notes.pop(msg.note)
                events.append(dict(track=ti, note=msg.note, start=start,
                                   duration=t - start, velocity=vel))
    return sorted(events, key=lambda e: e['start']), mid.length