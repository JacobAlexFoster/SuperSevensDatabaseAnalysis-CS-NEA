import sys
import sqlite3

# ============================================================
# CONNECT TO DATABASE
# ============================================================
conn = sqlite3.connect("tchoukball.db")
cursor = conn.cursor()

# ============================================================
# CREATE TABLES
# ============================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS clubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,
    total_games_played INTEGER DEFAULT 0,
    total_seasons INTEGER DEFAULT 0,
    current_season_ranking INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    total_wins INTEGER DEFAULT 0,
    total_losses INTEGER DEFAULT 0,
    total_games_played INTEGER DEFAULT 0,
    total_seasons INTEGER DEFAULT 0,
    FOREIGN KEY (club_id) REFERENCES clubs(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    number INTEGER,
    total_points INTEGER DEFAULT 0,
    seasons_played INTEGER DEFAULT 0,
    season_rating REAL DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    total_games_played INTEGER DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    season INTEGER NOT NULL,
    total_rounds INTEGER
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    tournament_id INTEGER,
    round_number INTEGER,
    stage TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id),
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);
""")

conn.commit()

# ============================================================
# INSERT DEFAULT TOURNAMENTS (IF EMPTY)
# ============================================================
cursor.execute("SELECT COUNT(*) FROM tournaments")
if cursor.fetchone()[0] == 0:
    cursor.executemany("""
        INSERT INTO tournaments (name, type, season, total_rounds)
        VALUES (?, ?, ?, ?)
    """, [
        ("National League", "league", 2024, 5),
        ("Regional League", "league", 2024, 4),
        ("Domini Fox Memorial", "event", 2024, 1),
        ("National Youth Finals", "finals", 2024, 1),
        ("National League Cup", "cup", 2024, 1),
        ("Finals Day", "finals", 2024, 1)
    ])
    conn.commit()

# ============================================================
# VIEW FUNCTIONS
# ============================================================
def view_players():
    cursor.execute("SELECT * FROM players")
    for row in cursor.fetchall():
        print(row)

def view_clubs():
    cursor.execute("SELECT * FROM clubs")
    for row in cursor.fetchall():
        print(row)

def view_teams():
    cursor.execute("SELECT * FROM teams")
    for row in cursor.fetchall():
        print(row)

def view_matches():
    cursor.execute("""
        SELECT matches.id, matches.season, matches.match_date,
               matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score,
               tournaments.name AS tournament_name,
               matches.round_number, matches.stage
        FROM matches
        LEFT JOIN tournaments ON matches.tournament_id = tournaments.id
    """)
    for row in cursor.fetchall():
        print(row)

# ============================================================
# TOURNAMENT SELECTION (ADMIN USE)
# ============================================================
def select_tournament():
    # Step 1: select tournament name
    cursor.execute("SELECT DISTINCT name FROM tournaments")
    tournament_names = cursor.fetchall()

    print("\nSelect tournament:")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    t_choice = int(input("Select: "))
    selected_name = tournament_names[t_choice - 1][0]

    # Step 2: select season for that tournament
    cursor.execute("SELECT DISTINCT season FROM tournaments WHERE name = ?", (selected_name,))
    seasons = cursor.fetchall()

    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    # Step 3: return exact tournament row
    cursor.execute("""
        SELECT id, name, total_rounds
        FROM tournaments
        WHERE name = ? AND season = ?
    """, (selected_name, selected_season))

    return cursor.fetchone()  # (id, name, total_rounds)

# ============================================================
# VIEW MATCHES BY TOURNAMENT + SEASON (USER USE)
# ============================================================
def view_matches_by_tournament_and_season():
    # Step 1: select tournament
    cursor.execute("SELECT DISTINCT name FROM tournaments")
    tournament_names = cursor.fetchall()

    print("\nSelect tournament:")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    t_choice = int(input("Select: "))
    selected_name = tournament_names[t_choice - 1][0]

    # Step 2: select season
    cursor.execute("SELECT DISTINCT season FROM tournaments WHERE name = ?", (selected_name,))
    seasons = cursor.fetchall()

    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    # Step 3: fetch matches
    cursor.execute("""
        SELECT matches.id, matches.match_date, matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score, matches.round_number
        FROM matches
        JOIN tournaments ON matches.tournament_id = tournaments.id
        WHERE tournaments.name = ? AND tournaments.season = ?
    """, (selected_name, selected_season))

    rows = cursor.fetchall()

    print(f"\n=== MATCHES FOR {selected_name} ({selected_season}) ===")
    for row in rows:
        print(row)
# ============================================================
def view_league_table_by_season():
    # Step 1: Select season
    cursor.execute("SELECT DISTINCT season FROM matches ORDER BY season")
    seasons = cursor.fetchall()

    if not seasons:
        print("No seasons found.")
        return

    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    # Step 2: Build league table
    cursor.execute("""
        SELECT
            teams.id,
            teams.name,
            SUM(CASE WHEN matches.home_team_id = teams.id AND matches.home_score > matches.away_score THEN 1
                     WHEN matches.away_team_id = teams.id AND matches.away_score > matches.home_score THEN 1
                     ELSE 0 END) AS wins,

            SUM(CASE WHEN matches.home_team_id = teams.id AND matches.home_score < matches.away_score THEN 1
                     WHEN matches.away_team_id = teams.id AND matches.away_score < matches.home_score THEN 1
                     ELSE 0 END) AS losses,

            SUM(CASE WHEN teams.id = matches.home_team_id THEN matches.home_score
                     WHEN teams.id = matches.away_team_id THEN matches.away_score
                     ELSE 0 END) AS goals_for,

            SUM(CASE WHEN teams.id = matches.home_team_id THEN matches.away_score
                     WHEN teams.id = matches.away_team_id THEN matches.home_score
                     ELSE 0 END) AS goals_against

        FROM teams
        LEFT JOIN matches
            ON teams.id = matches.home_team_id OR teams.id = matches.away_team_id
        WHERE matches.season = ?
        GROUP BY teams.id
    """, (selected_season,))

    rows = cursor.fetchall()

    if not rows:
        print("No matches found for that season.")
        return

    # Step 3: Sort table
    table = []
    for team_id, name, wins, losses, gf, ga in rows:
        wins = wins or 0
        losses = losses or 0
        gf = gf or 0
        ga = ga or 0
        gd = gf - ga
        table.append((name, wins, losses, gf, ga, gd))

    table.sort(key=lambda x: (-x[1], -x[5], -x[3]))  # wins desc, GD desc, GF desc

    # Step 4: Print table
    print(f"\n=== LEAGUE TABLE FOR SEASON {selected_season} ===")
    print("Pos | Team | Wins | Losses | GF | GA | GD")
    print("-------------------------------------------")

    pos = 1
    for row in table:
        name, wins, losses, gf, ga, gd = row
        print(f"{pos} | {name} | {wins} | {losses} | {gf} | {ga} | {gd}")
        pos += 1

# ============================================================
# ============================================================
# ============================================================
# ============================================================
# ============================================================

# ============================================================
# PROGRAM START
# ============================================================
print("""
TCHOUKBALL UK PROGRAM
OPTIONS
1 - LOGIN
2 - QUIT
""")

inp = int(input("select an input: "))

if inp == 1:
    prelog = int(input("Login as: 1 - admin, 2 - user: "))

    # ============================================================
    # ADMIN LOGIN
    # ============================================================
    if prelog == 1:
        if int(input("Enter password: ")) != 6969:
            print("Incorrect password.")
            sys.exit()

        print("LOGGED IN AS ADMIN")
        print("""
        OPTIONS:
        1 - player menu
        2 - club menu
        3 - match menu
        4 - team menu
        """)

        optSelect = int(input("select an option: "))

        # ============================================================
        # PLAYER MENU
        # ============================================================
        if optSelect == 1:
            print("""
            1 - add player
            2 - edit player
            3 - remove player
            """)
            choice = int(input("select: "))

            if choice == 1:
                plId = int(input("id: "))
                plName = input("name: ")
                plNumber = int(input("number: "))
                plTeamId = int(input("team id: "))
                plPoints = int(input("points: "))
                plSeasons = int(input("seasons: "))
                plWins = int(input("wins: "))
                plLosses = int(input("losses: "))
                plRating = float(input("rating: "))
                plGames = int(input("games: "))

                cursor.execute("""
                    INSERT INTO players (
                        id, team_id, name, number, total_points, seasons_played,
                        wins, losses, season_rating, total_games_played
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (plId, plTeamId, plName, plNumber, plPoints,
                      plSeasons, plWins, plLosses, plRating, plGames))
                conn.commit()
                print("Player added.")

            elif choice == 2:
                plid = int(input("player id: "))
                cursor.execute("SELECT * FROM players WHERE id = ?", (plid,))
                if cursor.fetchone() is None:
                    print("Player not found.")
                else:
                    print("""
                    1 - id
                    2 - name
                    3 - number
                    4 - team id
                    5 - points
                    6 - seasons
                    7 - wins
                    8 - losses
                    9 - rating
                    10 - games
                    """)
                    attr = int(input("attribute: "))
                    new = input("new value: ")

                    fields = {
                        1: "id",
                        2: "name",
                        3: "number",
                        4: "team_id",
                        5: "total_points",
                        6: "seasons_played",
                        7: "wins",
                        8: "losses",
                        9: "season_rating",
                        10: "total_games_played"
                    }

                    cursor.execute(f"UPDATE players SET {fields[attr]} = ? WHERE id = ?", (new, plid))
                    conn.commit()
                    print("Player updated.")

            elif choice == 3:
                plid = int(input("player id: "))
                cursor.execute("DELETE FROM players WHERE id = ?", (plid,))
                conn.commit()
                print("Player removed.")

        # ============================================================
        # CLUB MENU
        # ============================================================
        elif optSelect == 2:
            print("""
            1 - add club
            2 - edit club
            3 - remove club
            """)
            choice = int(input("select: "))

            if choice == 1:
                clubId = int(input("id: "))
                name = input("name: ")
                wins = int(input("wins: "))
                losses = int(input("losses: "))
                games = int(input("games: "))
                seasons = int(input("seasons: "))

                cursor.execute("""
                    INSERT INTO clubs (id, name, total_wins, total_losses, total_games_played, total_seasons)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (clubId, name, wins, losses, games, seasons))
                conn.commit()
                print("Club added.")

            elif choice == 2:
                clubId = int(input("club id: "))
                cursor.execute("SELECT * FROM clubs WHERE id = ?", (clubId,))
                if cursor.fetchone() is None:
                    print("Club not found.")
                else:
                    print("""
                    1 - id
                    2 - name
                    3 - wins
                    4 - losses
                    5 - games
                    6 - seasons
                    """)
                    attr = int(input("attribute: "))
                    new = input("new value: ")

                    fields = {
                        1: "id",
                        2: "name",
                        3: "total_wins",
                        4: "total_losses",
                        5: "total_games_played",
                        6: "total_seasons"
                    }

                    cursor.execute(f"UPDATE clubs SET {fields[attr]} = ? WHERE id = ?", (new, clubId))
                    conn.commit()
                    print("Club updated.")

            elif choice == 3:
                clubId = int(input("club id: "))
                cursor.execute("DELETE FROM clubs WHERE id = ?", (clubId,))
                conn.commit()
                print("Club removed.")

        # ============================================================
        # MATCH MENU
        # ============================================================
        elif optSelect == 3:
            print("""
            1 - add match
            2 - edit match
            3 - remove match
            """)
            choice = int(input("select: "))

            # ADD MATCH
            if choice == 1:
                matchId = int(input("id: "))
                season = int(input("season: "))
                date = input("date (YYYY-MM-DD): ")
                home = int(input("home team id: "))
                away = int(input("away team id: "))
                hscore = int(input("home score: "))
                ascore = int(input("away score: "))
                complete = int(input("completed? (1/0): "))

                tournament_id, tournament_name, total_rounds = select_tournament()

                round_number = None
                stage = None

                if total_rounds and total_rounds > 1:
                    round_number = int(input(f"Enter round (1-{total_rounds}): "))

                cursor.execute("""
                    INSERT INTO matches (
                        id, season, match_date, home_team_id, away_team_id,
                        home_score, away_score, is_completed,
                        tournament_id, round_number, stage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (matchId, season, date, home, away, hscore, ascore,
                      complete, tournament_id, round_number, stage))
                conn.commit()
                print("Match added.")

            # EDIT MATCH
            elif choice == 2:
                matchId = int(input("match id: "))
                cursor.execute("SELECT * FROM matches WHERE id = ?", (matchId,))
                if cursor.fetchone() is None:
                    print("Match not found.")
                else:
                    print("""
                    1 - id
                    2 - season
                    3 - date
                    4 - home team
                    5 - away team
                    6 - home score
                    7 - away score
                    8 - completed
                    9 - tournament
                    10 - round number
                    """)
                    attr = int(input("attribute: "))

                    if attr == 9:
                        tournament_id, _, _ = select_tournament()
                        cursor.execute("UPDATE matches SET tournament_id = ? WHERE id = ?", (tournament_id, matchId))
                    else:
                        new = input("new value: ")
                        fields = {
                            1: "id",
                            2: "season",
                            3: "match_date",
                            4: "home_team_id",
                            5: "away_team_id",
                            6: "home_score",
                            7: "away_score",
                            8: "is_completed",
                            10: "round_number"
                        }
                        cursor.execute(f"UPDATE matches SET {fields[attr]} = ? WHERE id = ?", (new, matchId))

                    conn.commit()
                    print("Match updated.")

            # REMOVE MATCH
            elif choice == 3:
                matchId = int(input("match id: "))
                cursor.execute("DELETE FROM matches WHERE id = ?", (matchId,))
                conn.commit()
                print("Match removed.")

        # ============================================================
        # TEAM MENU
        # ============================================================
        elif optSelect == 4:
            print("""
            1 - add team
            2 - edit team
            3 - remove team
            """)
            choice = int(input("select: "))

            if choice == 1:
                teamId = int(input("id: "))
                clubId = int(input("club id: "))
                name = input("name: ")
                wins = int(input("wins: "))
                losses = int(input("losses: "))
                games = int(input("games: "))
                seasons = int(input("seasons: "))

                cursor.execute("""
                    INSERT INTO teams (id, club_id, name, total_wins, total_losses, total_games_played, total_seasons)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (teamId, clubId, name, wins, losses, games, seasons))
                conn.commit()
                print("Team added.")

            elif choice == 2:
                teamId = int(input("team id: "))
                cursor.execute("SELECT * FROM teams WHERE id = ?", (teamId,))
                if cursor.fetchone() is None:
                    print("Team not found.")
                else:
                    print("""
                    1 - id
                    2 - name
                    3 - club id
                    4 - wins
                    5 - losses
                    6 - games
                    7 - seasons
                    """)
                    attr = int(input("attribute: "))
                    new = input("new value: ")

                    fields = {
                        1: "id",
                        2: "name",
                        3: "club_id",
                        4: "total_wins",
                        5: "total_losses",
                        6: "total_games_played",
                        7: "total_seasons"
                    }

                    cursor.execute(f"UPDATE teams SET {fields[attr]} = ? WHERE id = ?", (new, teamId))
                    conn.commit()
                    print("Team updated.")

            elif choice == 3:
                teamId = int(input("team id: "))
                cursor.execute("DELETE FROM teams WHERE id = ?", (teamId,))
                conn.commit()
                print("Team removed.")

    # ============================================================
    # USER MODE
    # ============================================================
    elif prelog == 2:
        print("""
        1 - view players
        2 - view clubs
        3 - view matches
        4 - view teams
        5 - view matches by tournament + season
        6 - view league table by season
        """)

        choice = int(input("select: "))

        if choice == 1:
            view_players()
        elif choice == 2:
            view_clubs()
        elif choice == 3:
            view_matches()
        elif choice == 4:
            view_teams()
        elif choice == 5:
            view_matches_by_tournament_and_season()
        elif choice == 6:
            view_league_table_by_season()
        else:
            sys.exit()
elif inp == 2:
    print("QUITTING")
    sys.exit()
