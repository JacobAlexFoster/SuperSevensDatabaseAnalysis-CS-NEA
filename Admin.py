import os
import sqlite3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(SCRIPT_DIR, "supersevens.db")


def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_players (
            match_id INTEGER,
            player_id INTEGER,
            points INTEGER DEFAULT 0,
            PRIMARY KEY (match_id, player_id),
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            number INTEGER NOT NULL,
            team_id INTEGER,
            club_id INTEGER,
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            home_club_id INTEGER NOT NULL,
            away_club_id INTEGER NOT NULL,
            home_team_id INTEGER NOT NULL,
            away_team_id INTEGER NOT NULL,
            home_score INTEGER NOT NULL,
            away_score INTEGER NOT NULL,
            match_date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def execute_query(query, params=()):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


def display_all(table_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    print(f"\n=== Current {table_name.capitalize()} ===")
    
    if table_name == "clubs":
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")
        else:
            print(f"{'ID':^6} | {'Club Name':^22} | {'Cumulative Points':^19}")
            print("-" * 55)
            for row in rows:
                print(f"{row[0]:^6} | {row[1]:^22} | {row[2]:^19}")
               
    elif table_name == "teams":
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")
        else:
            print(f"{'ID':^6} | {'Team Name':^22} | {'Cumulative Points':^19}")
            print("-" * 55)
            for row in rows:
                print(f"{row[0]:^6} | {row[1]:^22} | {row[2]:^19}")
               
    elif table_name == "players":
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.id,
                p.name AS player_name,
                p.number,
                t.name AS team_name,
                c.name AS club_name,
                COUNT(mp.match_id) AS total_appearances,
                TOTAL(mp.points) AS total_player_points
            FROM players p
            LEFT JOIN teams t ON p.team_id = t.id
            LEFT JOIN clubs c ON p.club_id = c.id
            LEFT JOIN match_players mp ON p.id = mp.player_id
            GROUP BY p.id
        """)
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")
        else:
            print(f"{'ID':^6} | {'Player Name':^26} | {'Number':^8} | {'Assigned Team':^22} | {'Assigned Club':^22} | {'Apps':^6} | {'Cumulative Pts':^17}")
            print("-" * 134)
            for row in rows:
                if row['team_name'] is not None:
                    t_name = row['team_name']
                else:
                    t_name = "N/A"
                if row['club_name'] is not None:
                    c_name = row['club_name']
                else:
                    c_name = "N/A"
                   
                apps = row['total_appearances']
                display_pts = int(row['total_player_points'])
                print(f"{row['id']:^6} | {row['player_name']:^26} | {row['number']:^8} | {t_name:^22} | {c_name:^22} | {apps:^6} | {display_pts:^17}")
               
    elif table_name == "matches":
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                m.id,
                m.match_date,
                hc.name AS home_club,
                ht.name AS home_team,
                m.home_score,
                m.away_score,
                at.name AS away_team,
                ac.name AS away_club
            FROM matches m
            JOIN clubs hc ON m.home_club_id = hc.id
            JOIN clubs ac ON m.away_club_id = ac.id
            JOIN teams ht ON m.home_team_id = ht.id
            JOIN teams at ON m.away_team_id = at.id
        """)
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")
        else:
            print(f"{'ID':^5} | {'Date':^12} | {'Home Club':^16} | {'Home Team':^23} | {'H-Score':^7} | {'A-Score':^7} | {'Away Team':^23} | {'Away Club':^16}")
            print("-" * 143)
            for row in rows:
                print(f"{row['id']:^5} | {row['match_date']:^12} | {row['home_club']:^16} | {row['home_team']:^23} | {row['home_score']:^7} | {row['away_score']:^7} | {row['away_team']:^23} | {row['away_club']:^16}")            
    conn.close()
    print("=" * 25)


def addclub():
    print("\n--- Clubs ---")
    club_name = input("input club name: ")
    execute_query("INSERT INTO clubs (name) VALUES (?)", (club_name,))
    print(f"Club '{club_name}' added successfully.")


def editclub():
    display_all("clubs")
    club_ID = int(input("input club id: "))
    new_name = input("input new club name: ")
    execute_query("UPDATE clubs SET name = ? WHERE id = ?", (new_name, club_ID))
    print("Club updated successfully.")


def removeclub():
    display_all("clubs")
    club_ID = int(input("input club id: "))
    execute_query("DELETE FROM clubs WHERE id = ?", (club_ID,))
    execute_query("DELETE FROM players WHERE club_id = ?", (club_ID,))
    print("Club and its registered players removed successfully.")


def listclub():
    display_all("clubs")


def clubedit():
    print("""
1 - add
2 - edit
3 - remove
4 - list""")
    choice = int(input("input an option: "))
    if choice == 1:
        addclub()
    elif choice == 2:
        editclub()
    elif choice == 3:
        removeclub()
    elif choice == 4:
        listclub()
    else:
        return


def addteam():
    print("\n--- Teams ---")
    team_name = input("input team name: ")
    execute_query("INSERT INTO teams (name) VALUES (?)", (team_name,))
    print(f"Team '{team_name}' added successfully.")


def editteam():
    display_all("teams")
    team_ID = int(input("input team id: "))
    new_name = input("input new team name: ")
    execute_query("UPDATE teams SET name = ? WHERE id = ?", (new_name, team_ID))
    print("Team updated successfully.")


def removeteam():
    display_all("teams")
    team_ID = int(input("input team id: "))
    execute_query("DELETE FROM teams WHERE id = ?", (team_ID,))
    execute_query("DELETE FROM players WHERE team_id = ?", (team_ID,))
    print("Team and its registered players removed successfully.")


def listteams():
    display_all("teams")


def teamedit():
    print("""
1 - add
2 - edit
3 - remove
4 - list""")
    choice = int(input("input an option: "))
    if choice == 1:
        addteam()
    elif choice == 2:
        editteam()
    elif choice == 3:
        removeteam()
    elif choice == 4:
        listteams()
    else:
        return


def addplayer():
    player_name = input("input players full name: ")
    player_number = int(input("input player number: "))
    display_all("clubs")
    club_id = int(input("Assign to Club ID: "))
    display_all("teams")
    team_id = int(input("Assign to Team ID: "))
    execute_query("""
        INSERT INTO players (name, number, club_id, team_id)
        VALUES (?, ?, ?, ?)
    """, (player_name, player_number, club_id, team_id))
    print(f"Player '{player_name}' added and assigned successfully.")
    display_all("players")


def editplayer():
    display_all("players")
    player_ID = int(input("input player id: "))
    print("""To edit:
1 - name
2 - number
3 - team
4 - club
5 - cancel""")
   
    tochange = int(input("Variable to change: "))
    if tochange == 1:
        new_name = input("input new full name: ")
        execute_query("UPDATE players SET name = ? WHERE id = ?", (new_name, player_ID))
        print("Player name updated successfully.")
    elif tochange == 2:
        newnumber = int(input("input new number: "))
        execute_query("UPDATE players SET number = ? WHERE id = ?", (newnumber, player_ID))
        print("Player number updated successfully.")
    elif tochange == 3:
        display_all("teams")
        newteam = int(input("input new team ID: "))
        execute_query("UPDATE players SET team_id = ? WHERE id = ?", (newteam, player_ID))
        print("Player team updated successfully.")
    elif tochange == 4:
        display_all("clubs")
        newclub = int(input("input new club ID: "))
        execute_query("UPDATE players SET club_id = ? WHERE id = ?", (newclub, player_ID))
        print("Player club updated successfully.")
    elif tochange == 5:
        return
    else:
        print("Invalid selection.")
        return


def removeplayer():
    display_all("players")
    player_ID = int(input("input player id: "))
    execute_query("DELETE FROM players WHERE id = ?", (player_ID,))
    execute_query("DELETE FROM match_players WHERE player_id = ?", (player_ID,))
    print("Player removed successfully.")


def listplayers():
    display_all("players")


def playeredit():
    print("""
1 - add
2 - edit
3 - remove
4 - list""")
    choice = int(input("input an option: "))
    if choice == 1:
        addplayer()
    elif choice == 2:
        editplayer()
    elif choice == 3:
        removeplayer()
    elif choice == 4:
        listplayers()
    else:
        return


def removeplayersfrommatch(match_id):
    print("\n=============================================")
    print(f"Removing Players from Match ID: {match_id}")
    print("=============================================")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    while True:
        cursor.execute("""
            SELECT p.id, p.name, p.number
            FROM match_players mp
            JOIN players p ON mp.player_id = p.id
            WHERE mp.match_id = ?
        """, (match_id,))
        current_roster = cursor.fetchall()
        if not current_roster:
            print("No players left on the roster for this match.")
            break
        print(f"\n{'Player ID':^10} | {'Current Match Roster':^25} | {'Squad No.':^10}")
        print("-" * 52)
        for p in current_roster:
            print(f"{p[0]:^10} | {p[1]:^25} | {p[2]:^10}")
        print("-" * 52)
        print("Type a Player's ID and press Enter to remove them from this match.")
        print("Type 0 when you are finished removing players.")
        try:
            player_id = int(input("Enter Player ID to remove (or 0 to finish): "))
            if player_id == 0:
                break
            if any(p[0] == player_id for p in current_roster):
                cursor.execute("""
                    DELETE FROM match_players
                    WHERE match_id = ? AND player_id = ?
                """, (match_id, player_id))
                conn.commit()
                print(f"Player ID {player_id} removed from the match roster.")
            else:
                print("That player is not on this match roster. Choose a valid ID.")
        except ValueError:
            print("Please enter a valid numeric ID.")
    conn.close()
    print("\nMatch roster updates saved successfully!")


def viewmatchroster():
    display_all("matches")
    match_ID = int(input("Enter Match ID to view its roster: "))
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.number, mp.points
        FROM match_players mp
        JOIN players p ON mp.player_id = p.id
        WHERE mp.match_id = ?
    """, (match_ID,))
    roster = cursor.fetchall()
    conn.close()
    print(f"\n=== Roster for Match ID: {match_ID} ===")
    if not roster:
        print("No players recorded for this match yet.")
    else:
        print(f"{'Player ID':^10} | {'Player Name':^22} | {'Squad No.':^10} | {'Match Points':^12}")
        print("-" * 65)
        for player in roster:
            print(f"{player[0]:^10} | {player[1]:^22} | {player[2]:^10} | {player[3]:^12}")
    print("=" * 25)


def addmatch():
    match_date = input("Enter Match Date (e.g., 2026-05-26): ")
    display_all("clubs")
    home_club_id = int(input("Enter Home Club ID: "))
    away_club_id = int(input("Enter Away Club ID: "))
    display_all("teams")
    home_team_id = int(input("Enter Home Team ID: "))
    away_team_id = int(input("Enter Away Team ID: "))
    homescore = int(input("Enter Home Score: "))
    awayscore = int(input("Enter Away Score: "))
   
    execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (homescore, home_club_id))
    execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (awayscore, away_club_id))
    execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (homescore, home_team_id))
    execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (awayscore, away_team_id))

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
   
    cursor.execute("""
        INSERT INTO matches (home_club_id, away_club_id, home_team_id, away_team_id, home_score, away_score, match_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (home_club_id, away_club_id, home_team_id, away_team_id, homescore, awayscore, match_date))
   
    new_match_id = cursor.lastrowid
   
    cursor.execute("SELECT id FROM players WHERE team_id = ? OR team_id = ?", (home_team_id, away_team_id))
    team_players = cursor.fetchall()
   
    for player in team_players:
        cursor.execute("""
            INSERT OR IGNORE INTO match_players (match_id, player_id, points)
            VALUES (?, ?, 0)
        """, (new_match_id, player[0]))
       
    conn.commit()
    conn.close()
       
    print(f"\nMatch recorded! All team players have been automatically added to the roster for Match ID: {new_match_id} with 0 pts.")
   
    addplayersinmatch(new_match_id, home_team_id, away_team_id)


def addplayersinmatch(match_id, home_team_id, away_team_id):
    print("\n=============================================")
    print(f"Match Scoring Center - Match ID: {match_id}")
    print("=============================================")
   
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT home_team_id, away_team_id, home_score, away_score
        FROM matches
        WHERE id = ?
    """, (match_id,))
    match_data = cursor.fetchone()
    conn.close()
   
    if match_data:
        home_team_id, away_team_id, home_max_score, away_max_score = match_data
    else:
        print("Error: Match data could not be retrieved.")
        return

    while True:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.number, mp.points, p.team_id
            FROM match_players mp
            JOIN players p ON mp.player_id = p.id
            WHERE mp.match_id = ?
        """, (match_id,))
        roster = cursor.fetchall()
        conn.close()
       
        if not roster:
            print("Notice: Roster is currently empty. Fetching registered team players...")
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM players WHERE team_id = ? OR team_id = ?", (home_team_id, away_team_id))
            team_players = cursor.fetchall()
            conn.close()
           
            if not team_players:
                print("\n[Database Error]: No players are assigned to these teams in your system.")
                print("Please go to 'player edit' -> 'add' to assign players to these Team IDs first.")
                return
               
            for player in team_players:
                execute_query("""
                    INSERT OR IGNORE INTO match_players (match_id, player_id, points)
                    VALUES (?, ?, 0)
                """, (match_id, player[0]))
           
            print("Team players successfully imported to match roster! Reloading interface...")
            continue
           
        home_allocated = sum(p[3] for p in roster if p[4] == home_team_id)
        away_allocated = sum(p[3] for p in roster if p[4] == away_team_id)
       
        home_remaining = home_max_score - home_allocated
        away_remaining = away_max_score - away_allocated
       
        print("\n=================== LIVE TRACKING ===================")
        print(f"Home Team Total Score: {home_max_score:^3} | Allocated: {home_allocated:^3} | Remaining: {home_remaining:^3}")
        print(f"Away Team Total Score: {away_max_score:^3} | Allocated: {away_allocated:^3} | Remaining: {away_remaining:^3}")
        print("=====================================================")
       
        print(f"\n{'ID':^6} | {'Player Name':^25} | {'Squad No.':^10} | {'Current Match Pts':^17}")
        print("-" * 67)
        for p in roster:
            print(f"{p[0]:^6} | {p[1]:^25} | {p[2]:^10} | {p[3]:^17}")
        print("-" * 67)
        print("Enter a Player's ID to input/update their score.")
        print("Type 0 when you are finished updating scores.")
       
        try:
            player_id = int(input("\nEnter Player ID (or 0 to finish): "))
            if player_id == 0:
                break
               
            chosen_player = next((p for p in roster if p[0] == player_id), None)
           
            if chosen_player:
                p_points = int(input(f"Enter points scored by Player ID {player_id}: "))
               
                execute_query("""
                    UPDATE match_players
                    SET points = ?
                    WHERE match_id = ? AND player_id = ?
                """, (p_points, match_id, player_id))
                print(f"Points updated successfully for Player ID {player_id}.")
            else:
                print("Invalid Player ID. Please pick a player listed on the roster table.")
        except ValueError:
            print("Please enter a valid numeric input.")
           
    print("\nMatch statistics locked and finalized!")


def editmatch():
    display_all("matches")
    match_ID = int(input("input match id: "))
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT home_club_id, away_club_id, home_team_id, away_team_id, home_score, away_score, match_date FROM matches WHERE id = ?", (match_ID,))
    match_data = cursor.fetchone()
    conn.close()
   
    if match_data is None:
        print("Match ID not found.")
        return
       
    old_h_club, old_a_club, old_h_team, old_a_team, old_h_score, old_a_score, old_date = match_data
   
    print("""To edit:
1 - date
2 - home club
3 - away club
4 - home team
5 - away team
6 - home score
7 - away score
8 - edit player points / add players
9 - remove players from roster
10 - cancel""")
    tochange = int(input("Variable to change: "))
   
    if tochange == 1:
        new_date = input("input new match date (e.g., 2026-05-26): ")
        execute_query("UPDATE matches SET match_date = ? WHERE id = ?", (new_date, match_ID))
        print("Match date updated successfully.")
       
    elif tochange == 2:
        display_all("clubs")
        new_h_club = int(input("input new Home Club ID: "))
        execute_query("UPDATE clubs SET points = points - ? WHERE id = ?", (old_h_score, old_h_club))
        execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (old_h_score, new_h_club))
        execute_query("UPDATE matches SET home_club_id = ? WHERE id = ?", (new_h_club, match_ID))
        print("Home Club updated and points transferred successfully.")
       
    elif tochange == 3:
        display_all("clubs")
        new_a_club = int(input("input new Away Club ID: "))
        execute_query("UPDATE clubs SET points = points - ? WHERE id = ?", (old_a_score, old_a_club))
        execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (old_a_score, new_a_club))
        execute_query("UPDATE matches SET away_club_id = ? WHERE id = ?", (new_a_club, match_ID))
        print("Away Club updated and points transferred successfully.")
       
    elif tochange == 4:
        display_all("teams")
        new_h_team = int(input("input new Home Team ID: "))
        execute_query("UPDATE teams SET points = points - ? WHERE id = ?", (old_h_score, old_h_team))
        execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (old_h_score, new_h_team))
        execute_query("UPDATE matches SET home_team_id = ? WHERE id = ?", (new_h_team, match_ID))
        execute_query("DELETE FROM match_players WHERE match_id = ?", (match_ID,))
        print("Notice: Match teams changed. Previous player roster for this match has been reset.")
        print("Home Team updated and points transferred successfully.")
       
    elif tochange == 5:
        display_all("teams")
        new_a_team = int(input("input new Away Team ID: "))
        execute_query("UPDATE teams SET points = points - ? WHERE id = ?", (old_a_score, old_a_team))
        execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (old_a_score, new_a_team))
        execute_query("UPDATE matches SET away_team_id = ? WHERE id = ?", (new_a_team, match_ID))
        execute_query("DELETE FROM match_players WHERE match_id = ?", (match_ID,))
        print("Notice: Match teams changed. Previous player roster for this match has been reset.")
        print("Away Team updated and points transferred successfully.")
       
    elif tochange == 6:
        new_h_score = int(input("input new Home Score: "))
        score_diff = new_h_score - old_h_score
        execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (score_diff, old_h_club))
        execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (score_diff, old_h_team))
        execute_query("UPDATE matches SET home_score = ? WHERE id = ?", (new_h_score, match_ID))
        print("Home score and table points updated successfully.")
       
    elif tochange == 7:
        new_a_score = int(input("input new Away Score: "))
        score_diff = new_a_score - old_a_score
        execute_query("UPDATE clubs SET points = points + ? WHERE id = ?", (score_diff, old_a_club))
        execute_query("UPDATE teams SET points = points + ? WHERE id = ?", (score_diff, old_a_team))
        execute_query("UPDATE matches SET away_score = ? WHERE id = ?", (new_a_score, match_ID))
        print("Away score and table points updated successfully.")
       
    elif tochange == 8:
        addplayersinmatch(match_ID, old_h_team, old_a_team)
       
    elif tochange == 9:
        removeplayersfrommatch(match_ID)
       
    elif tochange == 10:
        return
    else:
        print("Invalid selection.")
        return


def listmatch():
    display_all("matches")


def removematch():
    execute_query("""
        DELETE FROM match_players
        WHERE match_id NOT IN (SELECT id FROM matches)
    """)

    display_all("matches")
   
    user_input = input("Input match ID to remove (or press Enter to cancel code): ")
    if not user_input.strip():
        print("Player standings sweep completed successfully.")
        return

    match_ID = int(user_input)
   
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT home_club_id, away_club_id, home_team_id, away_team_id, home_score, away_score
        FROM matches
        WHERE id = ?
    """, (match_ID,))
    match_data = cursor.fetchone()
    conn.close()
   
    if match_data is None:
        print("Match ID not found.")
        return
       
    home_club, away_club, home_team, away_team, home_score, away_score = match_data
   
    execute_query("UPDATE clubs SET points = points - ? WHERE id = ?", (home_score, home_club))
    execute_query("UPDATE clubs SET points = points - ? WHERE id = ?", (away_score, away_club))
    execute_query("UPDATE teams SET points = points - ? WHERE id = ?", (home_score, home_team))
    execute_query("UPDATE teams SET points = points - ? WHERE id = ?", (away_score, away_team))
   
    execute_query("DELETE FROM matches WHERE id = ?", (match_ID,))
   
    execute_query("DELETE FROM match_players WHERE match_id = ?", (match_ID,))
   
    print(f"\nMatch {match_ID} removed successfully!")
    print(f"Subtracted {home_score} pts from Club {home_club}/Team {home_team}")
    print(f"Subtracted {away_score} pts from Club {away_club}/Team {away_team}.")


def matchedit():
    print("""
1 - add
2 - edit
3 - remove
4 - list matches
5 - view match roster
6 - cancel""")
    choice = int(input("input an option: "))
    if choice == 1:
        addmatch()
    elif choice == 2:
        editmatch()
    elif choice == 3:
        removematch()
    elif choice == 4:
        listmatch()
    elif choice == 5:
        viewmatchroster()
    else:
        return


def main():
    init_db()
    while True:
        print("""
=== MENU ===
1 - club edit
2 - team edit
3 - player edit
4 - match edit
5 - exit""")
        options = int(input("input an option: "))
        if options == 1:
            clubedit()
        elif options == 2:
            teamedit()
        elif options == 3:
            playeredit()
        elif options == 4:
            matchedit()
        elif options == 5:
            print("Exiting program.")
            break
        else:
            print("Invalid selection.")


if __name__ == "__main__":
    main()