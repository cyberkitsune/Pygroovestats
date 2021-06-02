import dataclasses


@dataclasses.dataclass
class GSScoreEntry:
    song_name: str
    chart_id: int
    game_id: int
    user_id: int
    user_name: str
    difficulty: str
    level: str
    play_mode: str
    score: float
    date_submitted: str
    is_gslaunch: bool
    comment: str = None


@dataclasses.dataclass
class GSSongInfo:
    song_name: str
    song_artist: str
    song_pack: str
    song_difficulty: str
    song_level: int
    song_steps: int
    song_holds: int
    song_mines: int
    song_jumps: int
    song_rolls: int
    cover_url: str


@dataclasses.dataclass
class GSJudgeInfo:
    fantastic: int
    excellent: int
    great: int
    decent: int
    wayoff: int
    miss: int
    boysoff: bool = False
    cmod: str = None


# Example: 1552e, 521g, 23d, 65wo, 170m, C1140
def parse_score_judges(score, total_notes):
    if not isinstance(score, GSScoreEntry):
        raise Exception("Not a GSScoreentry!")

    if score.comment is None:
        raise Exception("No comment data!")

    excellent = 0
    great = 0
    decent = 0
    wayoff = 0
    miss = 0
    boysoff = False
    cmod = None

    # FIXME This feels bad and maybe I should be using regex
    split = score.comment.split(", ")
    for element in split:
        if 'e' in element:
            excellent = int(element.strip('e'))

        if 'g' in element:
            great = int(element.strip('g'))

        if 'd' in element:
            decent = int(element.strip('d'))

        if 'wo' in element:
            wayoff = int(element.strip('wo'))

        if 'm' in element:
            miss = int(element.strip('m'))

        if 'C' in element:
            cmod = element

        if 'No Dec/WO' in element:
            boysoff = True

    if boysoff:
        fantastic = total_notes - excellent - great - miss
    else:
        fantastic = total_notes - excellent - great - decent - wayoff - miss

    return GSJudgeInfo(fantastic=fantastic, excellent=excellent, great=great, decent=decent, wayoff=wayoff,
                        miss=miss, boysoff=boysoff, cmod=cmod)




def diff_to_id(diff):
    if diff == "Easy":
        return 4
    elif diff == "Medium":
        return 3
    elif diff == 'Hard':
        return 2
    elif diff == 'Expert':
        return 1

    return 1


def id_to_diff(did):
    diffs = ["Expert", "Hard", "Medium", "Easy"]
    return diffs[did - 1]


def id_to_mode(mid):
    modes = ['Sgl', 'Dbl']
    return modes[mid - 1]
