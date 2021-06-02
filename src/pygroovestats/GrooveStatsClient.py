import requests, dataclasses, urllib.parse
from bs4 import BeautifulSoup
from .GrooveStatsUtils import GSScoreEntry, GSSongInfo, id_to_mode, id_to_diff, diff_to_id


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

        user_name = ''
        bio_heads = soup.find_all(class_="bio_head")
        for head in bio_heads:
            if head.text == "User Name:":
                user_name = head.next_sibiling

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
            si = GSScoreEntry(song_name=first_col_items[0].text, chart_id=chart_id, game_id=game_id, difficulty=diff,
                              level=level, play_mode=mode,
                              score=float(cols[1].text), date_submitted=cols[3].text, user_id=userid,
                              is_gslaunch=is_gslaunch, user_name=user_name)

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
            cmt_text = None
            acro = cols[3].find('acronym')
            if acro is not None:
                cmt_text = acro.get('title')
            else:
                cmt_text = cols[3].text
            si = GSScoreEntry(song_name=song_name, chart_id=chartid, game_id=gameid, difficulty=diff, level=level,
                              play_mode=mode,
                              score=float(cols[2].text), date_submitted=cols[5].text, user_id=int(userid),
                              is_gslaunch=is_gslaunch, comment=cmt_text, user_name=cols[1].text)

            rows.append(si)

        return rows

    def song_info(self, chartid, gameid, modeid, typeid=1):
        page = self.__get_page('songscores', {'chartid': chartid, 'gameid': gameid, 'modeid': modeid, 'typeid': typeid})
        soup = BeautifulSoup(page, 'html5lib')

        song_name = soup.find(class_="ranking_head").text
        song_artist = ''
        song_pack = ''
        song_difficulty = ''
        song_level = 0
        song_steps = 0
        song_holds = 0
        song_mines = 0
        song_jumps = 0
        song_rolls = 0
        cover_url = ''

        # First, get song data
        sdata = soup.find(id="ranking_options", class_="scores_detail_summary").find_all('tr')
        for row in sdata:
            cols = row.find_all('td')
            text = cols[0].text
            if text == "Artist:":
                song_artist = cols[1].text
            if text == "Mode:":
                song_difficulty = cols[1].text
            if text == "Pack:":
                song_pack = cols[1].text
            if text == "Difficulty:":
                song_level = int(cols[1].text)
            if text == "Jumps:":
                song_jumps = int(cols[1].text)
            if text == "Holds:":
                song_holds = int(cols[1].text)
            if text == "Mines:":
                song_mines = int(cols[1].text)
            if text == "Rolls:":
                song_rolls = int(cols[1].text)
            if text == "Steps:":
                song_steps = int(cols[1].text)

        cover = soup.find(id="ranking_options", class_="scores_detail_banner").find('img')
        if cover is not None:
            cover_url = cover.get('src')

        return GSSongInfo(song_name=song_name, song_artist=song_artist, song_pack=song_pack,
                          song_difficulty=song_difficulty, song_level=song_level, song_steps=song_steps,
                          song_holds=song_holds, song_mines=song_mines, song_jumps=song_jumps, song_rolls=song_rolls,
                          cover_url=cover_url)

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
