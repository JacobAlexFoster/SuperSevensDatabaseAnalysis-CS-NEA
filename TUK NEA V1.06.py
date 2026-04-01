
import sys
import sqlite3

# ============================================================#
conn = sqlite3.connect("tchoukball.db")
cursor = conn.cursor()
# ============================================================#

# ============================================================# clubs table
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

# ============================================================# teams table
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

# ============================================================# players table
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

# ============================================================# tournaments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tournaments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    season INTEGER NOT NULL,
    total_rounds INTEGER
);
""")

# ============================================================# matches table
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

# ============================================================# player seasons table
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

# ============================================================# match players table
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

# ============================================================# inserting default tournaments
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

# ============================================================# view all players function
def view_players():
    print("\n=== ALL PLAYERS ===")
    print("ID | Team ID | Name | Number | Total Points | Seasons Played | Season Rating | Wins | Losses | Games Played")
    print("-" * 110)
    cursor.execute("SELECT * FROM players ORDER BY team_id ASC, name ASC")
    for row in cursor.fetchall():
        print(row)

# ============================================================# view all clubs function
def view_clubs():
    print("\n=== ALL CLUBS ===")
    print("ID | Name | Wins | Losses | Games Played | Seasons | Current Ranking")
    print("-" * 70)
    cursor.execute("SELECT * FROM clubs ORDER BY name ASC")
    for row in cursor.fetchall():
        print(row)

# ============================================================# view all teams function
def view_teams():
    print("\n=== ALL TEAMS ===")
    print("ID | Club ID | Name | Wins | Losses | Games Played | Seasons")
    print("-" * 60)
    cursor.execute("SELECT * FROM teams ORDER BY club_id ASC, name ASC")
    for row in cursor.fetchall():
        print(row)

# ============================================================# view all matches function
def view_matches():
    print("\n=== ALL MATCHES (Newest First) ===")
    print("ID | Season | Date | Home Team | Away Team | Home Score | Away Score | Tournament | Round | Stage")
    print("-" * 100)
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

# ============================================================# select tournament function
def select_tournament():
    cursor.execute("SELECT DISTINCT name FROM tournaments ORDER BY name ASC")
    tournament_names = cursor.fetchall()
    print("\n=== SELECT TOURNAMENT ===")
    for i, t in enumerate(tournament_names, start=1):
        print(f"{i} - {t[0]}")
    t_choice = int(input("Select tournament: "))
    selected_name = tournament_names[t_choice - 1][0]
    
    cursor.execute("SELECT DISTINCT season FROM tournaments WHERE name = ? ORDER BY season DESC", (selected_name,))
    seasons = cursor.fetchall()
    print("\nSelect season:")
    for i, s in enumerate(seasons, start=1):
        print(f"{i} - {s[0]}")
    s_choice = int(input("Select season: "))
    selected_season = seasons[s_choice - 1][0]
    
    cursor.execute("SELECT id, name, total_rounds FROM tournaments WHERE name = ? AND season = ?", (selected_name, selected_season))
    return cursor.fetchone()

# ============================================================# view matches by tournament function
def view_matches_by_tournament_and_season():
    tournament_info = select_tournament()
    if not tournament_info:
        print("Tournament not found.")
        return
    
    t_id, t_name, _ = tournament_info
    cursor.execute("""
        SELECT matches.id, matches.match_date, matches.home_team_id, matches.away_team_id,
               matches.home_score, matches.away_score, matches.round_number
        FROM matches
        WHERE tournament_id = ?
        ORDER BY matches.match_date DESC
    """, (t_id,))
    rows = cursor.fetchall()
    print(f"\n=== MATCHES FOR {t_name} ===")
    print("ID | Date | Home Team | Away Team | Home Score | Away Score | Round")
    print("-" * 70)
    for row in rows:
        print(row)

# ============================================================# view league table function
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
        SELECT teams.id, teams.name,
            SUM(CASE WHEN matches.home_team_id = teams.id AND matches.home_score > matches.away_score THEN 1
                     WHEN matches.away_team_id = teams.id AND matches.away_score > matches.home_score THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN matches.home_team_id = teams.id AND matches.home_score < matches.away_score THEN 1
                     WHEN matches.away_team_id = teams.id AND matches.away_score < matches.home_score THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN teams.id = matches.home_team_id THEN matches.home_score
                     WHEN teams.id = matches.away_team_id THEN matches.away_score ELSE 0 END) AS goals_for,
            SUM(CASE WHEN teams.id = matches.home_team_id THEN matches.away_score
                     WHEN teams.id = matches.away_team_id THEN matches.home_score ELSE 0 END) AS goals_against
        FROM teams
        LEFT JOIN matches ON teams.id = matches.home_team_id OR teams.id = matches.away_team_id
        WHERE matches.season = ?
        GROUP BY teams.id
    """, (selected_season,))
    
    rows = cursor.fetchall()
    if not rows:
        print("No matches found.")
        return
    
    table = []
    for team_id, name, wins, losses, gf, ga in rows:
        gf, ga = gf or 0, ga or 0
        table.append((name, wins or 0, losses or 0, gf, ga, gf - ga))
    
    table.sort(key=lambda x: (-x[1], -x[5], -x[3]))
    print(f"\n=== LEAGUE TABLE — SEASON {selected_season} ===")
    print("Pos | Team | Wins | Losses | GF | GA | GD")
    for i, row in enumerate(table, 1):
        print(f"{i} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")

# ============================================================# assign players to match function
def assign_players_to_match(match_id, team_id):
    print(f"\nAssign players for team {team_id} in match {match_id}")
    cursor.execute("SELECT id, name FROM players WHERE team_id = ? ORDER BY name ASC", (team_id,))
    players = cursor.fetchall()
    if not players:
        print("No players found.")
        return
    for p in players: print(f"{p[0]} - {p[1]}")
    ids = input("Enter player IDs (comma separated): ").split(",")
    for pid in ids:
        pid = pid.strip()
        if pid:
            cursor.execute("INSERT INTO match_players (match_id, player_id) VALUES (?, ?)", (match_id, pid))
    conn.commit()

# ============================================================# update stats after match function
def update_player_stats_after_match(match_id):
    cursor.execute("SELECT home_team_id, away_team_id, home_score, away_score, season FROM matches WHERE id = ?", (match_id,))
    match = cursor.fetchone()
    if not match: return
    
    h_team, a_team, h_score, a_score, season = match
    winner = h_team if h_score > a_score else (a_team if a_score > h_score else None)
    
    cursor.execute("SELECT player_id FROM match_players WHERE match_id = ?", (match_id,))
    for (p_id,) in cursor.fetchall():
        cursor.execute("SELECT team_id FROM players WHERE id = ?", (p_id,))
        p_team = cursor.fetchone()[0]
        
        # Update General Player Stats
        cursor.execute("UPDATE players SET total_games_played = total_games_played + 1 WHERE id = ?", (p_id,))
        cursor.execute("UPDATE player_seasons SET games = games + 1 WHERE player_id = ? AND season = ?", (p_id, season))
        
        # Update Win/Loss
        if winner:
            col = "wins" if p_team == winner else "losses"
            cursor.execute(f"UPDATE players SET {col} = {col} + 1 WHERE id = ?", (p_id,))
            cursor.execute(f"UPDATE player_seasons SET {col} = {col} + 1 WHERE player_id = ? AND season = ?", (p_id, season))

    # Update Team/Club totals
    for t_id in [h_team, a_team]:
        cursor.execute("UPDATE teams SET total_games_played = total_games_played + 1 WHERE id = ?", (t_id,))
        cursor.execute("SELECT club_id FROM teams WHERE id = ?", (t_id,))
        c_id = cursor.fetchone()[0]
        cursor.execute("UPDATE clubs SET total_games_played = total_games_played + 1 WHERE id = ?", (c_id,))
        if winner:
            t_col = "total_wins" if t_id == winner else "total_losses"
            cursor.execute(f"UPDATE teams SET {t_col} = {t_col} + 1 WHERE id = ?", (t_id,))
            cursor.execute(f"UPDATE clubs SET {t_col} = {t_col} + 1 WHERE id = ?", (c_id,))
    
    conn.commit()

# ============================================================# start new season function
def start_new_season():
    new_season = int(input("Enter new season year: "))
    t_list = [("National League", "league", new_season, 5), ("Regional League", "league", new_season, 4)]
    cursor.executemany("INSERT INTO tournaments (name, type, season, total_rounds) VALUES (?, ?, ?, ?)", t_list)
    
    cursor.execute("SELECT id FROM players")
    for (p_id,) in cursor.fetchall():
        cursor.execute("INSERT INTO player_seasons (player_id, season) VALUES (?, ?)", (p_id, new_season))
    
    cursor.execute("UPDATE players SET seasons_played = seasons_played + 1, wins = 0, losses = 0, total_games_played = 0")
    conn.commit()
    print(f"Season {new_season} started!")

# ============================================================# main program loop
while True:
    print("\nTCHOUKBALL UK PROGRAM\n1 - LOGIN\n2 - QUIT")
    try:
        inp = int(input("Select: "))
    except ValueError: continue

    if inp == 2:
        print("QUITTING")
        sys.exit()

    if inp == 1:
        prelog = int(input("1 - Admin, 2 - User: "))
        
        # ============================================================# admin login
        if prelog == 1:
            if int(input("Password: ")) != 6969:
                print("Incorrect.")
                continue
            
            while True:
                print("\nADMIN MENU\n1-Player, 2-Club, 3-Match, 4-Team, 5-New Season, 6-Back")
                opt = int(input("Option: "))
                if opt == 6: break
                
                # ============================================================# player menu
                if opt == 1:
                    while True:
                        print("\nPLAYER MENU\n1-Add, 2-Edit, 3-Remove, 4-Back")
                        c = int(input("Select: "))
                        if c == 4: break
                        if c == 1:
                            data = (int(input("ID: ")), int(input("TeamID: ")), input("Name: "), int(input("No: ")))
                            cursor.execute("INSERT INTO players (id, team_id, name, number) VALUES (?,?,?,?)", data)
                            conn.commit()
                        elif c == 3:
                            cursor.execute("DELETE FROM players WHERE id = ?", (int(input("ID: ")),))
                            conn.commit()
                
                # ============================================================# club menu
                elif opt == 2:
                    while True:
                        print("\nCLUB MENU\n1-Add, 2-Edit, 3-Remove, 4-Back")
                        c = int(input("Select: "))
                        if c == 4: break
                        if c == 1:
                            cursor.execute("INSERT INTO clubs (id, name) VALUES (?, ?)", (int(input("ID: ")), input("Name: ")))
                            conn.commit()

                # ============================================================# match menu
                elif opt == 3:
                    while True:
                        print("\nMATCH MENU\n1-Add, 2-Edit, 3-Remove, 4-Back")
                        c = int(input("Select: "))
                        if c == 4: break
                        if c == 1:
                            m_id = int(input("ID: "))
                            t_info = select_tournament()
                            cursor.execute("""INSERT INTO matches (id, season, match_date, home_team_id, away_team_id, tournament_id) 
                                           VALUES (?,?,?,?,?,?)""", 
                                           (m_id, t_info[1], input("Date: "), int(input("Home ID: ")), int(input("Away ID: ")), t_info[0]))
                            conn.commit()
                            assign_players_to_match(m_id, int(input("Home ID: ")))
                            update_player_stats_after_match(m_id)

                # ============================================================# team menu
                elif opt == 4:
                    while True:
                        print("\nTEAM MENU\n1-Add, 2-Edit, 3-Remove, 4-Back")
                        c = int(input("Select: "))
                        if c == 4: break
                        if c == 1:
                            cursor.execute("INSERT INTO teams (id, club_id, name) VALUES (?, ?, ?)", 
                                           (int(input("ID: ")), int(input("Club ID: ")), input("Name: ")))
                            conn.commit()

                # ============================================================# start new season
                elif opt == 5:
                    start_new_season()

        # ============================================================# user login
        elif prelog == 2:
            while True:
                print("\nUSER MENU\n1-Players, 2-Clubs, 3-Teams, 4-Matches, 5-Tourney View, 6-Table, 7-Back")
                c = int(input("Select: "))
                if c == 7: break
                elif c == 1: view_players()
                elif c == 2: view_clubs()
                elif c == 3: view_teams()
                elif c == 4: view_matches()
                elif c == 5: view_matches_by_tournament_and_season()
                elif c == 6: view_league_table_by_season()
