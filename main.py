from GrooveStatsClient import GrooveStatsClient
from GrooveStatsUtils import diff_to_id, parse_score_judges


def main():
    gsc = GrooveStatsClient()
    recent = gsc.get_recent(66782)
    print(recent)
    most_recent = recent[0]
    detailed = gsc.get_detailed_for(most_recent)
    print(detailed)
    song_info = gsc.song_info(detailed.chart_id, detailed.game_id, diff_to_id(detailed.difficulty))
    print(parse_score_judges(detailed, song_info.song_steps + song_info.song_holds + song_info.song_rolls + (song_info.song_jumps)))


if __name__ == "__main__":
    main()