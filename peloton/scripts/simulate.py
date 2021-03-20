#!/usr/bin/env python
from peloton.models.bolid import Peloton
from peloton.models.track import Track, Sector


class Race:
    track: Track
    peloton: Peloton

    def __init__(self, track: Track, peloton: Peloton):
        self.track = track
        self.peloton = peloton

    def run(self):
        pass


if __name__ == "__main__":
    sectors = (
        Sector(length=200)
    )
    race = Race()
