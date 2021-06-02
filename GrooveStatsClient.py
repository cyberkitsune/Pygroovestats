import requests, dataclasses, urllib.parse
from bs4 import BeautifulSoup


@dataclasses.dataclass
class GSScoreEntry:
    song_name: str
    chart_id: int
    game_id: int
    user_id: int
    difficulty: str
    level: str
    play_mode: str
    score: float
    date_submitted: str
    is_gslaunch: bool
    comment: str = None


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


class NoGSDetailException(Exception):
    pass


class GrooveStatsClient(object):
    def __init__(self):
        self.headers = {}
        self.base_url = "https://groovestats.com/"

    def __get_page(self, page, args=None):
        if args is None:
            args = {}

        args['page'] = page
        r = requests.get(self.base_url, headers=self.headers, params=args)

        if r.status_code != 200:
            raise Exception("Web request returned %i!" % r.status_code)

        return r.content

    def get_recent(self, userid):
        page = self.__get_page('profile', {'id': userid})
        soup = BeautifulSoup(page, 'html5lib')

        table = soup.find(id='ranking_scores', class_='bio_recent_scores').find_all('tr')
        rows = []
        for row in table:
            cols = row.find_all('td')
            if (len(cols)) != 4:
                continue

            if cols[0].text == 'Song Name':
                continue

            first_col_items = cols[0].find_all('a')
            diff, level, mode = first_col_items[1].text.split()
            parsed = urllib.parse.urlparse(first_col_items[0].get('href'))
            chart_id = urllib.parse.parse_qs(parsed.query)['chartid'][0]
            game_id = urllib.parse.parse_qs(parsed.query)['gameid'][0]

            is_gslaunch = False
            img_tag = cols[1].find('img')
            if img_tag is not None:
                if 'autoverify' in img_tag.get('src'):
                    is_gslaunch = True
            si = GSScoreEntry(song_name=first_col_items[0].text, chart_id=chart_id, game_id=game_id, difficulty=diff, level=level, play_mode=mode,
                              score=float(cols[1].text), date_submitted=cols[3].text, user_id=userid, is_gslaunch=is_gslaunch)

            rows.append(si)

        return rows

    def song_scores(self, chartid, gameid, modeid, typeid=1):
        page = self.__get_page('songscores', {'chartid': chartid, 'gameid': gameid, 'modeid': modeid, 'typeid': typeid})
        soup = BeautifulSoup(page, 'html5lib')

        difficulty = 0
        song_name = soup.find(class_="ranking_head").text
        # First, get song data
        sdata = soup.find(id="ranking_options", class_="scores_detail_summary").find_all('tr')
        for row in sdata:
            cols = row.find_all('td')
            if cols[0].text == "Difficulty:":
                difficulty = int(cols[1].text)

        table = soup.find(id='ranking_scores', class_='scores_detail_scores').find_all('tr')
        rows = []
        for row in table:
            cols = row.find_all('td')
            if (len(cols)) != 6:
                continue

            if cols[0].text == '#':
                continue

            name_element = cols[1].find('a')
            parsed = urllib.parse.urlparse(name_element.get('href'))
            userid = urllib.parse.parse_qs(parsed.query)['id'][0]
            diff, level, mode = (id_to_diff(modeid), '(%i)' % difficulty, id_to_mode(typeid))

            is_gslaunch = False
            img_tag = cols[2].find('img')
            if img_tag is not None:
                if 'autoverify' in img_tag.get('src'):
                    is_gslaunch = True
            si = GSScoreEntry(song_name=song_name, chart_id=chartid, game_id=gameid, difficulty=diff, level=level, play_mode=mode,
                              score=float(cols[2].text), date_submitted=cols[5].text, user_id=int(userid), is_gslaunch=is_gslaunch, comment=cols[3].text)

            rows.append(si)

        return rows

    def get_detailed_for(self, scoreentry):
        if not isinstance(scoreentry, GSScoreEntry):
            raise Exception("You need to call this against a GSScoreEntry!")

        if not scoreentry.is_gslaunch:
            raise NoGSDetailException("Score was not submitted with GSLauncher")

        if scoreentry.comment is not None:
            return scoreentry

        all_song_scores = self.song_scores(scoreentry.chart_id, scoreentry.game_id, diff_to_id(scoreentry.difficulty))
        found = None
        for score in all_song_scores:
            if score.user_id == scoreentry.user_id and score.score == scoreentry.score:
                found = score

        if found is None:
            raise Exception("Unable to find detailed score on song score list?")

        return found
