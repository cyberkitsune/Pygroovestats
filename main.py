from GrooveStatsClient import GrooveStatsClient, diff_to_id


def main():
    gsc = GrooveStatsClient()
    recent = gsc.get_recent(66782)
    print(recent)
    most_recent = recent[0]
    detailed = gsc.get_detailed_for(most_recent)
    print(detailed)


if __name__ == "__main__":
    main()