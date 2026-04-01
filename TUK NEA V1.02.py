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
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season INTEGER NOT NULL,
    match_date TEXT NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER DEFAULT 0,
    away_score INTEGER DEFAULT 0,
    is_completed INTEGER DEFAULT 0,
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);
""")

conn.commit()

# ============================================================
# VIEW FUNCTIONS
# ============================================================
def view_players():
    cursor.execute("""
        SELECT id, team_id, name, number, total_points,
               seasons_played, season_rating, wins, losses,
               total_games_played
        FROM players
    """)
    rows = cursor.fetchall()
    print("\n=== ALL PLAYERS ===")
    for row in rows:
        print(row)


def view_clubs():
    cursor.execute("""
        SELECT id, name, total_wins, total_losses,
               total_games_played, total_seasons,
               current_season_ranking
        FROM clubs
    """)
    rows = cursor.fetchall()
    print("\n=== ALL CLUBS ===")
    for row in rows:
        print(row)


def view_matches():
    cursor.execute("""
        SELECT id, season, match_date, home_team_id,
               away_team_id, home_score, away_score,
               is_completed
        FROM matches
    """)
    rows = cursor.fetchall()
    print("\n=== ALL MATCHES ===")
    for row in rows:
        print(row)


def view_teams():
    cursor.execute("""
        SELECT id, club_id, name, total_wins, total_losses,
               total_games_played, total_seasons
        FROM teams
    """)
    rows = cursor.fetchall()
    print("\n=== ALL TEAMS ===")
    for row in rows:
        print(row)


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
        print("ADMIN LOGIN")
        login = int(input("Enter password: "))

        if login == 6969:
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
                print("player menu")
                print("""
                1 - add player
                2 - edit player
                3 - remove player
                """)

                secondroundopt = int(input("select an option: "))

                # ADD PLAYER
                if secondroundopt == 1:
                    print("adding player")
                    plId = int(input("enter player id: "))
                    plName = input("enter player name: ")
                    plNumber = int(input("enter player number: "))
                    plTeamId = int(input("enter player team id: "))
                    plPoints = int(input("enter player points: "))
                    plSeasons = int(input("enter player seasons: "))
                    plWins = int(input("enter player wins: "))
                    plLosses = int(input("enter player losses: "))
                    plRating = float(input("enter player rating this season: "))
                    plGames = int(input("enter player games: "))

                    cursor.execute("""
                        INSERT INTO players (
                            id, team_id, name, number, total_points,
                            seasons_played, wins, losses, season_rating,
                            total_games_played
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        plId, plTeamId, plName, plNumber, plPoints,
                        plSeasons, plWins, plLosses, plRating, plGames
                    ))

                    conn.commit()
                    print("Player added successfully!")

                # EDIT PLAYER
                elif secondroundopt == 2:
                    plid = int(input("player id to edit: "))
                    cursor.execute("SELECT * FROM players WHERE id = ?", (plid,))
                    player = cursor.fetchone()

                    if player is None:
                        print("Player not found.")
                    else:
                        print("""
                        attributes to edit:
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

                        toEdit = int(input("attribute to edit: "))

                        fields = {
                            1: ("id", int),
                            2: ("name", str),
                            3: ("number", int),
                            4: ("team_id", int),
                            5: ("total_points", int),
                            6: ("seasons_played", int),
                            7: ("wins", int),
                            8: ("losses", int),
                            9: ("season_rating", float),
                            10: ("total_games_played", int)
                        }

                        if toEdit in fields:
                            col, cast = fields[toEdit]
                            newVal = cast(input(f"new {col}: "))
                            cursor.execute(f"UPDATE players SET {col} = ? WHERE id = ?", (newVal, plid))
                            conn.commit()
                            print("Player updated successfully!")
                        else:
                            print("Invalid option.")
                            sys.exit()

                # REMOVE PLAYER
                elif secondroundopt == 3:
                    print("removing player")
                    removePL = int(input("player id to remove: "))

                    cursor.execute("SELECT * FROM players WHERE id = ?", (removePL,))
                    player = cursor.fetchone()

                    if player is None:
                        print("Player not found.")
                    else:
                        cursor.execute("DELETE FROM players WHERE id = ?", (removePL,))
                        conn.commit()
                        print("Player removed successfully!")

                else:
                    print("error, exiting...")
                    sys.exit()

            # ============================================================
            # CLUB MENU
            # ============================================================
            elif optSelect == 2:
                print("club menu")
                print("""
                1 - add club
                2 - edit club
                3 - remove club
                """)

                secondroundopt = int(input("select an option: "))

                # ADD CLUB
                if secondroundopt == 1:
                    print("adding club")
                    clubId = int(input("enter club id: "))
                    clubName = input("enter club name: ")
                    clubWins = int(input("enter club wins: "))
                    clubLosses = int(input("enter club losses: "))
                    clubGames = int(input("enter club N.O games: "))
                    clubSeasons = int(input("enter club N.O seasons: "))

                    cursor.execute("""
                        INSERT INTO clubs (
                            id, name, total_wins, total_losses,
                            total_games_played, total_seasons
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (clubId, clubName, clubWins, clubLosses, clubGames, clubSeasons))

                    conn.commit()
                    print("Club added successfully!")

                # EDIT CLUB
                elif secondroundopt == 2:
                    clubEdit = int(input("enter club id to edit: "))
                    cursor.execute("SELECT * FROM clubs WHERE id = ?", (clubEdit,))
                    club = cursor.fetchone()

                    if club is None:
                        print("Club not found.")
                    else:
                        print("""
                        attributes to edit:
                        1 - id
                        2 - name
                        3 - wins
                        4 - losses
                        5 - games
                        6 - seasons
                        """)

                        attributeEdit = int(input("select an attribute to edit: "))

                        fields = {
                            1: ("id", int),
                            2: ("name", str),
                            3: ("total_wins", int),
                            4: ("total_losses", int),
                            5: ("total_games_played", int),
                            6: ("total_seasons", int)
                        }

                        if attributeEdit in fields:
                            col, cast = fields[attributeEdit]
                            newVal = cast(input(f"new {col}: "))
                            cursor.execute(f"UPDATE clubs SET {col} = ? WHERE id = ?", (newVal, clubEdit))
                            conn.commit()
                            print("Club updated successfully!")
                        else:
                            print("Invalid option.")
                            sys.exit()

                # REMOVE CLUB
                elif secondroundopt == 3:
                    print("removing club")
                    removeClub = int(input("club id to remove: "))

                    cursor.execute("SELECT * FROM clubs WHERE id = ?", (removeClub,))
                    club = cursor.fetchone()

                    if club is None:
                        print("Club not found.")
                    else:
                        cursor.execute("DELETE FROM clubs WHERE id = ?", (removeClub,))
                        conn.commit()
                        print("Club removed successfully!")

                else:
                    print("error, exiting...")
                    sys.exit()

            # ============================================================
            # MATCH MENU
            # ============================================================
            elif optSelect == 3:
                print("match menu")
                print("""
                1 - add match
                2 - edit match
                3 - remove match
                """)

                secondroundopt = int(input("select an option: "))

                # ADD MATCH
                if secondroundopt == 1:
                    print("adding match")
                    matchId = int(input("enter match id: "))
                    matchSeason = int(input("enter match season: "))
                    matchDate = input("enter match date (YYYY-MM-DD): ")
                    matchHome = int(input("enter match home team id: "))
                    matchAway = int(input("enter match away team id: "))
                    matchHomeScore = int(input("enter match home score: "))
                    matchAwayScore = int(input("enter match away score: "))
                    matchIsComplete = int(input("enter match completion (1 = complete, 0 = not complete): "))

                    cursor.execute("""
                        INSERT INTO matches (
                            id, season, match_date, home_team_id, away_team_id,
                            home_score, away_score, is_completed
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        matchId, matchSeason, matchDate, matchHome, matchAway,
                        matchHomeScore, matchAwayScore, matchIsComplete
                    ))

                    conn.commit()
                    print("Match added successfully!")

                # EDIT MATCH
                elif secondroundopt == 2:
                    print("editing match")
                    matchEdit = int(input("enter match id to edit: "))

                    cursor.execute("SELECT * FROM matches WHERE id = ?", (matchEdit,))
                    match = cursor.fetchone()

                    if match is None:
                        print("Match not found.")
                    else:
                        print("""
                        attributes to edit:
                        1 - id
                        2 - season
                        3 - match date
                        4 - home team id
                        5 - away team id
                        6 - home score
                        7 - away score
                        8 - completion status (1 = complete, 0 = not complete)
                        """)

                        attributeEdit = int(input("select an attribute to edit: "))

                        fields = {
                            1: ("id", int),
                            2: ("season", int),
                            3: ("match_date", str),
                            4: ("home_team_id", int),
                            5: ("away_team_id", int),
                            6: ("home_score", int),
                            7: ("away_score", int),
                            8: ("is_completed", int)
                        }

                        if attributeEdit in fields:
                            col, cast = fields[attributeEdit]
                            newVal = cast(input(f"new {col}: "))
                            cursor.execute(f"UPDATE matches SET {col} = ? WHERE id = ?", (newVal, matchEdit))
                            conn.commit()
                            print("Match updated successfully!")
                        else:
                            print("Invalid option.")
                            sys.exit()

                # REMOVE MATCH
                elif secondroundopt == 3:
                    print("removing match")
                    removeMatch = int(input("match id to remove: "))

                    cursor.execute("SELECT * FROM matches WHERE id = ?", (removeMatch,))
                    match = cursor.fetchone()

                    if match is None:
                        print("Match not found.")
                    else:
                        cursor.execute("DELETE FROM matches WHERE id = ?", (removeMatch,))
                        conn.commit()
                        print("Match removed successfully!")

                else:
                    print("error, exiting...")
                    sys.exit()

            # ============================================================
            # TEAM MENU
            # ============================================================
            elif optSelect == 4:
                print("team menu")
                print("""
                1 - add team
                2 - edit team
                3 - remove team
                """)

                secondroundopt = int(input("select an option: "))

                # ADD TEAM
                if secondroundopt == 1:
                    print("adding team")
                    teamId = int(input("enter team id: "))
                    clubId = int(input("enter club id that team belongs to: "))
                    teamName = input("enter team name: ")
                    teamWins = int(input("enter team wins: "))
                    teamLosses = int(input("enter team losses: "))
                    teamGames = int(input("enter team games: "))
                    teamSeasons = int(input("enter team seasons: "))

                    cursor.execute("""
                        INSERT INTO teams (
                            id, club_id, name, total_wins, total_losses,
                            total_games_played, total_seasons
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        teamId, clubId, teamName, teamWins, teamLosses,
                        teamGames, teamSeasons
                    ))

                    conn.commit()
                    print("Team added successfully!")

                # EDIT TEAM
                elif secondroundopt == 2:
                    teamEdit = int(input("enter team id to edit: "))

                    cursor.execute("SELECT * FROM teams WHERE id = ?", (teamEdit,))
                    team = cursor.fetchone()

                    if team is None:
                        print("Team not found.")
                    else:
                        print("""
                        attributes to edit:
                        1 - id
                        2 - name
                        3 - club id
                        4 - wins
                        5 - losses
                        6 - games
                        7 - seasons
                        """)

                        attributeEdit = int(input("select an attribute to edit: "))

                        fields = {
                            1: ("id", int),
                            2: ("name", str),
                            3: ("club_id", int),
                            4: ("total_wins", int),
                            5: ("total_losses", int),
                            6: ("total_games_played", int),
                            7: ("total_seasons", int)
                        }

                        if attributeEdit in fields:
                            col, cast = fields[attributeEdit]
                            newVal = cast(input(f"new {col}: "))
                            cursor.execute(f"UPDATE teams SET {col} = ? WHERE id = ?", (newVal, teamEdit))
                            conn.commit()
                            print("Team updated successfully!")
                        else:
                            print("Invalid option.")
                            sys.exit()

                # REMOVE TEAM
                elif secondroundopt == 3:
                    print("removing team")
                    removeTeam = int(input("team id to remove: "))

                    cursor.execute("SELECT * FROM teams WHERE id = ?", (removeTeam,))
                    team = cursor.fetchone()

                    if team is None:
                        print("Team not found.")
                    else:
                        cursor.execute("DELETE FROM teams WHERE id = ?", (removeTeam,))
                        conn.commit()
                        print("Team removed successfully!")

                else:
                    print("error, exiting...")
                    sys.exit()

            else:
                print("error, exiting...")
                sys.exit()

    # ============================================================
    # USER MODE
    # ============================================================
    elif prelog == 2:
        print("USER LOGIN")
        print("""
        OPTIONS:
        1 - view players
        2 - view clubs
        3 - view matches
        4 - view teams
        5 - view stats
        6 - view leaderboard
        7 - search club / players
        8 - filter team / club / season / ranking
        """)

        optSelect = int(input("select an option: "))

        if optSelect == 1:
            view_players()
        elif optSelect == 2:
            view_clubs()
        elif optSelect == 3:
            view_matches()
        elif optSelect == 4:
            view_teams()
        elif optSelect == 5:
            print("view stats")
        elif optSelect == 6:
            print("view leaderboard")
        elif optSelect == 7:
            print("view club / player")
        elif optSelect == 8:
            print("filter by team / club / season / ranking")
        else:
            print("error, exiting...")
            sys.exit()

elif inp == 2:
    print("QUITTING")
    sys.exit()

else:
    print("error")
 