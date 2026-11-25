import math
import os
import struct
import wave
import pygame


class MusicPlayer:
    """Manages audio playlist loading, playback controls, and track state."""

    SUPPORTED_EXTENSIONS = (".wav", ".mp3", ".ogg")

    def __init__(self, music_dir: str):
        self.music_dir = music_dir
        os.makedirs(self.music_dir, exist_ok=True)
        self._ensure_sample_tracks()

        self.playlist = self._load_playlist()
        self.current_index = 0
        self.is_playing = False
        self.track_lengths: dict[str, float] = {}
        self._preload_lengths()

    def _ensure_sample_tracks(self) -> None:
        """Creates two short WAV tones if the music directory has no audio files."""
        existing = [
            f for f in os.listdir(self.music_dir)
            if f.lower().endswith(self.SUPPORTED_EXTENSIONS)
        ]
        if existing:
            return

        samples = [
            ("track1.wav", 440.0, 6.0),  # 6-second A4 tone
            ("track2.wav", 523.25, 6.0),  # 6-second C5 tone
        ]
        sample_rate = 44100
        for filename, freq, duration in samples:
            filepath = os.path.join(self.music_dir, filename)
            num_samples = int(sample_rate * duration)
            with wave.open(filepath, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                frames = bytearray()
                for i in range(num_samples):
                    val = int(12000 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                    frames.extend(struct.pack("<h", val))
                wf.writeframes(bytes(frames))

    def _load_playlist(self) -> list[str]:
        """Returns sorted list of full file paths in music_dir."""
        files = sorted(
            f for f in os.listdir(self.music_dir)
            if f.lower().endswith(self.SUPPORTED_EXTENSIONS)
        )
        return [os.path.join(self.music_dir, f) for f in files]

    def _preload_lengths(self) -> None:
        """Caches track durations using pygame.mixer.Sound."""
        for path in self.playlist:
            try:
                self.track_lengths[path] = pygame.mixer.Sound(path).get_length()
            except pygame.error:
                self.track_lengths[path] = 0.0

    @property
    def current_track_path(self) -> str | None:
        if not self.playlist:
            return None
        return self.playlist[self.current_index]

    @property
    def current_track_name(self) -> str:
        path = self.current_track_path
        return os.path.basename(path) if path else "No tracks found"

    def play(self) -> None:
        """Loads and plays the current track from the beginning."""
        path = self.current_track_path
        if not path:
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self) -> None:
        """Stops playback."""
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self) -> None:
        """Advances to the next track (wraps around) and starts playing."""
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self) -> None:
        """Goes to the previous track (wraps around) and starts playing."""
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def update(self) -> None:
        """Updates playback state if a track finishes naturally."""
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.is_playing = False

    def get_progress(self) -> tuple[float, float]:
        """Returns (elapsed_seconds, total_seconds) for the active track."""
        path = self.current_track_path
        if not path:
            return 0.0, 0.0
        total = self.track_lengths.get(path, 0.0)
        if not self.is_playing:
            return 0.0, total
        pos_ms = pygame.mixer.music.get_pos()
        elapsed = max(0.0, pos_ms / 1000.0)
        return elapsed, total