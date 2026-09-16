class Playlist:
    def __init__(self):
        self.songs = []

    def add_song(self, name, duration):
        song = {
            "name": name,
            "duration": duration
        }

        self.songs.append(song)

    def remove_song(self, name):
        for song in self.songs:
            if song["name"] == name:
                self.songs.remove(song)
                return

        print("Песня не найдена")

    def total_duration(self):
        total = 0

        for song in self.songs:
            total += song["duration"]

        return total

    def __len__(self):
        return len(self.songs)

    def show_songs(self):
        for song in self.songs:
            print(song["name"], "-", song["duration"], "сек.")


playlist = Playlist()

playlist.add_song("Song 1", 200)
playlist.add_song("Song 2", 300)
playlist.add_song("Song 3", 150)

playlist.show_songs()

print("Количество песен:", len(playlist))
print("Общая длительность:", playlist.total_duration())

playlist.remove_song("Song 2")

playlist.show_songs()

playlist.remove_song("Несуществующая песня")