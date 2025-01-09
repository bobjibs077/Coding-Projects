import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pygame import mixer
import threading
import time

# Initialize the mixer
mixer.init()

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x400")
        self.root.config(bg="#1e1e2f")  # Dark background
        self.current_track = None
        self.is_playing = False
        self.track_length = 0
        self.stop_thread = False
        self.playlist = []

        # Styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#444", foreground="white", font=("Arial", 10), borderwidth=1)
        style.configure("TLabel", background="#1e1e2f", foreground="white", font=("Arial", 12))
        style.configure("TScale", background="#1e1e2f")
        style.configure("Treeview", background="#333", fieldbackground="#333", foreground="white")

        # Playlist Frame
        playlist_frame = tk.Frame(root, bg="#2e2e3f", relief="sunken", bd=2)
        playlist_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.playlist_box = ttk.Treeview(playlist_frame, columns=("Track"), show="headings", height=15)
        self.playlist_box.heading("Track", text="Playlist")
        self.playlist_box.pack(fill="both", expand=True)
        self.playlist_box.bind("<Double-1>", self.select_track)

        # Controls Frame
        controls_frame = tk.Frame(root, bg="#1e1e2f")
        controls_frame.pack(side="bottom", fill="x", pady=10)

        # Track Label
        self.label = ttk.Label(root, text="No Track Selected", anchor="center", wraplength=500)
        self.label.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=500, command=self.seek_track)
        self.progress.pack(pady=10)

        # Buttons
        self.play_button = ttk.Button(controls_frame, text="▶ Play", command=self.play_music)
        self.play_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(controls_frame, text="⏸ Pause", command=self.pause_music)
        self.pause_button.pack(side="left", padx=5)

        self.resume_button = ttk.Button(controls_frame, text="⏯ Resume", command=self.resume_music)
        self.resume_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(controls_frame, text="⏹ Stop", command=self.stop_music)
        self.stop_button.pack(side="left", padx=5)

        self.add_button = ttk.Button(controls_frame, text="➕ Add", command=self.add_to_playlist)
        self.add_button.pack(side="left", padx=5)

        # Volume Slider
        volume_frame = tk.Frame(root, bg="#1e1e2f")
        volume_frame.pack(pady=5)
        self.volume_label = ttk.Label(volume_frame, text="Volume")
        self.volume_label.pack(side="left", padx=5)
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=1, orient="horizontal", length=200, command=self.set_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side="left", padx=5)

    def add_to_playlist(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")])
        for file_path in file_paths:
            self.playlist.append(file_path)
            self.playlist_box.insert("", "end", values=(os.path.basename(file_path),))

    def select_track(self, event):
        selected = self.playlist_box.selection()
        if selected:
            index = self.playlist_box.index(selected[0])
            self.current_track = self.playlist[index]
            self.label.config(text=os.path.basename(self.current_track))
            mixer.music.load(self.current_track)
            self.play_music()

    def play_music(self):
        if self.current_track:
            mixer.music.play()
            self.is_playing = True
            self.track_length = mixer.Sound(self.current_track).get_length()
            threading.Thread(target=self.update_progress, daemon=True).start()
        else:
            messagebox.showwarning("Warning", "Please select a track first.")

    def pause_music(self):
        mixer.music.pause()
        self.is_playing = False

    def resume_music(self):
        mixer.music.unpause()
        self.is_playing = True

    def stop_music(self):
        mixer.music.stop()
        self.is_playing = False
        self.stop_thread = True
        self.progress.set(0)

    def set_volume(self, volume):
        mixer.music.set_volume(float(volume))

    def seek_track(self, value):
        if self.is_playing:
            mixer.music.rewind()
            mixer.music.set_pos(float(value) * self.track_length / 100)

    def update_progress(self):
        while self.is_playing:
            if self.stop_thread:
                self.stop_thread = False
                break
            current_time = mixer.music.get_pos() / 1000
            self.progress.set((current_time / self.track_length) * 100 if self.track_length > 0 else 0)
            time.sleep(1)

# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
