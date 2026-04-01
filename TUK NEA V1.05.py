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

cursor.execute("""
CREATE TABLE IF NOT EXISTS player_seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    games INTEGER DEFAULT 0,
    rating REAL DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS match_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    points INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES players(id)
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
    print("\n=== ALL PLAYERS ===")
    print("ID | Team ID | Name | Number | Total Points | Seasons Played | Season Rating | Wins | Losses | Games Played")
    print("-----------------------------------------------------------------------------------------------------------")

    cursor.execute("SELECT * FROM players ORDER BY team_id ASC, name ASC")
    for row in cursor.fetchall():
        print(row)

def view_clubs():
    print("\n=== ALL CLUBS ===")
    print("ID | Name | Wins | Losses | Games Played | Seasons | Current Ranking")
    print("---------------------------------------------------------------------")

    cursor.execute("SELECT * FROM clubs ORDER BY name ASC")
    for row in cursor.fetchall():
        print(row)

def view_teams():
    print("\n=== ALL TEAMS ===")
    print("ID | Club ID | Name | Wins | Losses | Games Played | Seasons")
    print("------------------------------------------------------------")

    cursor.execute("SELECT * FROM teams ORDER BY club_id ASC, name ASC")
    for row in cursor.fetchall():
        print(row)

def view_matches():
    print("\n=== ALL MATCHES (Newest First) ===")
    print("ID | Season | Date | Home Team | Away Team | Home Score | Away Score | Tournament | Round | Stage")
    print("--------------------------------------------------------------------------------------------------")

    cursor.execute("""
        SELECT matches.id, matches.season, matches.match_date,
               matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score,
               tournaments.name AS tournament_name,
               matches.round_number, matches.stage
        FROM matches
        LEFT JOIN tournaments ON matches.tournament_id = tournaments.id
        ORDER BY matches.season DESC, matches.match_date DESC
    """)
    for row in cursor.fetchall():
        print(row)

# ============================================================
# TOURNAMENT SELECTION
# ============================================================
def select_tournament():
    cursor.execute("SELECT DISTINCT name FROM tournaments ORDER BY name ASC")
    tournament_names = cursor.fetchall()

    print("\n=== SELECT TOURNAMENT ===")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    print("\nSelect tournament:")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    t_choice = int(input("Select: "))
    selected_name = tournament_names[t_choice - 1][0]

    cursor.execute(
        "SELECT DISTINCT season FROM tournaments WHERE name = ? ORDER BY season DESC",
        (selected_name,)
    )
    seasons = cursor.fetchall()

    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    cursor.execute("""
        SELECT id, name, total_rounds
        FROM tournaments
        WHERE name = ? AND season = ?
    """, (selected_name, selected_season))

    return cursor.fetchone()

# ============================================================
# VIEW MATCHES BY TOURNAMENT + SEASON (USER USE)
# ============================================================
def view_matches_by_tournament_and_season():
    cursor.execute("SELECT DISTINCT name FROM tournaments ORDER BY name ASC")
    tournament_names = cursor.fetchall()

    print("\n=== SELECT TOURNAMENT ===")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    t_choice = int(input("Select: "))
    selected_name = tournament_names[t_choice - 1][0]

    cursor.execute(
        "SELECT DISTINCT season FROM tournaments WHERE name = ? ORDER BY season DESC",
        (selected_name,)
    )
    seasons = cursor.fetchall()

    print("\n=== SELECT SEASON ===")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    cursor.execute("""
        SELECT matches.id, matches.match_date, matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score, matches.round_number
        FROM matches
        JOIN tournaments ON matches.tournament_id = tournaments.id
        WHERE tournaments.name = ? AND tournaments.season = ?
        ORDER BY matches.match_date DESC
    """, (selected_name, selected_season))

    rows = cursor.fetchall()

    print(f"\n=== MATCHES FOR {selected_name} ({selected_season}) ===")
    print("ID | Date | Home Team | Away Team | Home Score | Away Score | Round")
    print("--------------------------------------------------------------------")

    for row in rows:
        print(row)

    print("\n=== SELECT TOURNAMENT ===")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")

    t_choice = int(input("Select: "))
    selected_name = tournament_names[t_choice - 1][0]

    # Get seasons for that tournament
    cursor.execute(
        "SELECT DISTINCT season FROM tournaments WHERE name = ? ORDER BY season DESC",
        (selected_name,)
    )
    seasons = cursor.fetchall()

    print("\n=== SELECT SEASON ===")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

    # Fetch matches
    cursor.execute("""
        SELECT matches.id, matches.match_date, matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score, matches.round_number
        FROM matches
        JOIN tournaments ON matches.tournament_id = tournaments.id
        WHERE tournaments.name = ? AND tournaments.season = ?
        ORDER BY matches.match_date DESC
    """, (selected_name, selected_season))

    rows = cursor.fetchall()

    print(f"\n=== MATCHES FOR {selected_name} ({selected_season}) ===")
    for row in rows:
        print(row)

# ============================================================
# LEAGUE TABLE BY SEASON
# ============================================================
def view_league_table_by_season():
    cursor.execute("SELECT DISTINCT season FROM matches ORDER BY season DESC")
    seasons = cursor.fetchall()

    if not seasons:
        print("No seasons found.")
        return

    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")

    s_choice = int(input("Select: "))
    selected_season = seasons[s_choice - 1][0]

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

    table = []
    for team_id, name, wins, losses, gf, ga in rows:
        wins = wins or 0
        losses = losses or 0
        gf = gf or 0
        ga = ga or 0
        gd = gf - ga
        table.append((name, wins, losses, gf, ga, gd))

    table.sort(key=lambda x: (-x[1], -x[5], -x[3]))

    print(f"\n=== LEAGUE TABLE — SEASON {selected_season} ===")
    print("Pos | Team | Wins | Losses | Goals For | Goals Against | Goal Difference")
    print("--------------------------------------------------------------------------")


    pos = 1
    for row in table:
        name, wins, losses, gf, ga, gd = row
        print(f"{pos} | {name} | {wins} | {losses} | {gf} | {ga} | {gd}")
        pos += 1

# ============================================================
# ASSIGN PLAYERS TO MATCH
# ============================================================
def assign_players_to_match(match_id, team_id):
    print(f"\nAssign players for team {team_id} in match {match_id}")

    cursor.execute("SELECT id, name FROM players WHERE team_id = ? ORDER BY name ASC", (team_id,))
    players = cursor.fetchall()

    if not players:
        print("No players found for this team.")
        return

    print("Players:")
    for p in players:
        print(f"{p[0]} - {p[1]}")

    print("Enter player IDs who played (comma separated):")
    ids = input("Players: ").split(",")

    for pid in ids:
        pid = pid.strip()
        if not pid:
            continue
        cursor.execute("""
            INSERT INTO match_players (match_id, player_id)
            VALUES (?, ?)
        """, (match_id, pid))

    conn.commit()

# ============================================================
# UPDATE PLAYER, TEAM, CLUB STATS AFTER MATCH
# ============================================================
def update_player_stats_after_match(match_id):
    cursor.execute("""
        SELECT home_team_id, away_team_id, home_score, away_score, season
        FROM matches
        WHERE id = ?
    """, (match_id,))
    match = cursor.fetchone()

    if not match:
        print("Match not found for stat update.")
        return

    home_team, away_team, home_score, away_score, season = match

    if home_score > away_score:
        winner = home_team
        loser = away_team
    elif away_score > home_score:
        winner = away_team
        loser = home_team
    else:
        winner = None
        loser = None

    cursor.execute("""
        SELECT player_id FROM match_players
        WHERE match_id = ? AND player_id IN (SELECT id FROM players WHERE team_id = ?)
    """, (match_id, home_team))
    home_players = cursor.fetchall()

    cursor.execute("""
        SELECT player_id FROM match_players
        WHERE match_id = ? AND player_id IN (SELECT id FROM players WHERE team_id = ?)
    """, (match_id, away_team))
    away_players = cursor.fetchall()

    all_players = home_players + away_players

    # PLAYER STATS
    for (player_id,) in all_players:
        cursor.execute("""
            UPDATE players
            SET total_games_played = total_games_played + 1
            WHERE id = ?
        """, (player_id,))
            # UPDATE PLAYER RATING (points ÷ games)
    cursor.execute("""
        UPDATE players
        SET season_rating = 
            CASE 
                WHEN total_games_played > 0 THEN CAST(total_points AS FLOAT) / total_games_played
                ELSE 0
            END
        WHERE id = ?
    """, (player_id,))


    cursor.execute("""
            UPDATE player_seasons
            SET games = games + 1
            WHERE player_id = ? AND season = ?
        """, (player_id, season))

    if winner == home_team and (player_id,) in home_players:
            cursor.execute("UPDATE players SET wins = wins + 1 WHERE id = ?", (player_id,))
            cursor.execute("""
                UPDATE player_seasons SET wins = wins + 1
                WHERE player_id = ? AND season = ?
            """, (player_id, season))
    elif winner == away_team and (player_id,) in away_players:
            cursor.execute("UPDATE players SET wins = wins + 1 WHERE id = ?", (player_id,))
            cursor.execute("""
                UPDATE player_seasons SET wins = wins + 1
                WHERE player_id = ? AND season = ?
            """, (player_id, season))
    else:
            cursor.execute("UPDATE players SET losses = losses + 1 WHERE id = ?", (player_id,))
            cursor.execute("""
                UPDATE player_seasons SET losses = losses + 1
                WHERE player_id = ? AND season = ?
            """, (player_id, season))

    # TEAM STATS
    cursor.execute("UPDATE teams SET total_games_played = total_games_played + 1 WHERE id = ?", (home_team,))
    cursor.execute("UPDATE teams SET total_games_played = total_games_played + 1 WHERE id = ?", (away_team,))

    if winner == home_team:
        cursor.execute("UPDATE teams SET total_wins = total_wins + 1 WHERE id = ?", (home_team,))
        cursor.execute("UPDATE teams SET total_losses = total_losses + 1 WHERE id = ?", (away_team,))
    elif winner == away_team:
        cursor.execute("UPDATE teams SET total_wins = total_wins + 1 WHERE id = ?", (away_team,))
        cursor.execute("UPDATE teams SET total_losses = total_losses + 1 WHERE id = ?", (home_team,))

    # CLUB STATS
    cursor.execute("SELECT club_id FROM teams WHERE id = ?", (home_team,))
    home_club = cursor.fetchone()[0]

    cursor.execute("SELECT club_id FROM teams WHERE id = ?", (away_team,))
    away_club = cursor.fetchone()[0]

    cursor.execute("UPDATE clubs SET total_games_played = total_games_played + 1 WHERE id = ?", (home_club,))
    cursor.execute("UPDATE clubs SET total_games_played = total_games_played + 1 WHERE id = ?", (away_club,))

    if winner == home_team:
        cursor.execute("UPDATE clubs SET total_wins = total_wins + 1 WHERE id = ?", (home_club,))
        cursor.execute("UPDATE clubs SET total_losses = total_losses + 1 WHERE id = ?", (away_club,))
    elif winner == away_team:
        cursor.execute("UPDATE clubs SET total_wins = total_wins + 1 WHERE id = ?", (away_club,))
        cursor.execute("UPDATE clubs SET total_losses = total_losses + 1 WHERE id = ?", (home_club,))

    conn.commit()
    print("Player, team, and club stats updated for match", match_id)

# ============================================================
# START NEW SEASON
# ============================================================
def start_new_season():
    new_season = int(input("Enter new season year: "))

    tournaments = [
        ("National League", "league", new_season, 5),
        ("Regional League", "league", new_season, 4),
        ("Domini Fox Memorial", "event", new_season, 1),
        ("National Youth Finals", "finals", new_season, 1),
        ("National League Cup", "cup", new_season, 1),
        ("Finals Day", "finals", new_season, 1)
    ]

    cursor.executemany("""
        INSERT INTO tournaments (name, type, season, total_rounds)
        VALUES (?, ?, ?, ?)
    """, tournaments)

    cursor.execute("SELECT id FROM players")
    players = cursor.fetchall()

    for (player_id,) in players:
        cursor.execute("""
            INSERT INTO player_seasons (player_id, season)
            VALUES (?, ?)
        """, (player_id, new_season))

    cursor.execute("""
        UPDATE players
        SET seasons_played = seasons_played + 1
    """)

    cursor.execute("""
        UPDATE players
        SET season_rating = 0,
            wins = 0,
            losses = 0,
            total_games_played = 0
    """)

    conn.commit()
    print(f"Season {new_season} started successfully!")

# ============================================================
# PROGRAM START
# ============================================================
while True:
    print("""
    TCHOUKBALL UK PROGRAM
    OPTIONS
    1 - LOGIN
    2 - QUIT
    """)

    inp = int(input("select an input: "))

    if inp == 2:
        print("QUITTING")
        sys.exit()

    if inp == 1:
        prelog = int(input("Login as: 1 - admin, 2 - user: "))

        # ============================================================
        # ADMIN LOGIN
        # ============================================================
        if prelog == 1:
            if int(input("Enter password: ")) != 6969:
                print("Incorrect password.")
                continue

            print("LOGGED IN AS ADMIN")

            # ---------------- ADMIN MENU LOOP ----------------
            while True:
                print("""
                ADMIN MENU
                1 - player menu
                2 - club menu
                3 - match menu
                4 - team menu
                5 - start new season
                6 - Return
                """)

                optSelect = int(input("select an option: "))

                if optSelect == 6:
                    break

                # ============================================================
                # PLAYER MENU
                # ============================================================
                if optSelect == 1:
                    while True:
                        print("""
                        PLAYER MENU
                        1 - add player
                        2 - edit player
                        3 - remove player
                        4 - Return
                        """)

                        choice = int(input("select: "))

                        if choice == 4:
                            break

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
                    while True:
                        print("""
                        CLUB MENU
                        1 - add club
                        2 - edit club
                        3 - remove club
                        4 - Return
                        """)

                        choice = int(input("select: "))

                        if choice == 4:
                            break

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
                    while True:
                        print("""
                        MATCH MENU
                        1 - add match
                        2 - edit match
                        3 - remove match
                        4 - Return
                        """)

                        choice = int(input("select: "))

                        if choice == 4:
                            break

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

                            assign_players_to_match(matchId, home)
                            assign_players_to_match(matchId, away)
                            update_player_stats_after_match(matchId)

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
                                update_player_stats_after_match(matchId)

                        elif choice == 3:
                            matchId = int(input("match id: "))
                            cursor.execute("DELETE FROM match_players WHERE match_id = ?", (matchId,))
                            cursor.execute("DELETE FROM matches WHERE id = ?", (matchId,))
                            conn.commit()
                            print("Match and related player links removed.")

                # ============================================================
                # TEAM MENU
                # ============================================================
                elif optSelect == 4:
                    while True:
                        print("""
                        TEAM MENU
                        1 - add team
                        2 - edit team
                        3 - remove team
                        4 - Return
                        """)

                        choice = int(input("select: "))

                        if choice == 4:
                            break

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
                                2 - club id
                                3 - name
                                4 - wins
                                5 - losses
                                6 - games
                                7 - seasons
                                """)
                                attr = int(input("attribute: "))
                                new = input("new value: ")

                                fields = {
                                    1: "id",
                                    2: "club_id",
                                    3: "name",
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
                # START NEW SEASON (ADMIN MENU OPTION 5)
                # ============================================================
                elif optSelect == 5:
                    start_new_season()

        # ============================================================
        # USER LOGIN
        # ============================================================
        elif prelog == 2:
            while True:
                print("""
                USER MENU
                1 - view players
                2 - view clubs
                3 - view teams
                4 - view matches
                5 - view matches by tournament + season
                6 - view league table by season
                7 - Return
                """)

                choice = int(input("select: "))

                if choice == 7:
                    break
                elif choice == 1:
                    view_players()
                elif choice == 2:
                    view_clubs()
                elif choice == 3:
                    view_teams()
                elif choice == 4:
                    view_matches()
                elif choice == 5:
                    view_matches_by_tournament_and_season()
                elif choice == 6:
                    view_league_table_by_season()
                