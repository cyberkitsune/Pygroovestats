import sys, urllib.parse
from pygroovestats.GrooveStatsUtils import diff_to_id, parse_score_judges
from pygroovestats.GrooveStatsClient import GrooveStatsClient


def main():
    gsc = GrooveStatsClient()
    recent = gsc.get_recent(66793)
    print(recent)
    most_recent = recent[0]
    detailed = gsc.get_detailed_for(most_recent)
    print(detailed)
    song_info = gsc.song_info(detailed.chart_id, detailed.game_id, diff_to_id(detailed.difficulty))
    print(song_info)
    print("https://assets.cyberkitsune.net/gstats_proxy/%s" % urllib.parse.quote(song_info.cover_url))
    print(parse_score_judges(detailed, song_info.song_steps))


if __name__ == "__main__":
    main()