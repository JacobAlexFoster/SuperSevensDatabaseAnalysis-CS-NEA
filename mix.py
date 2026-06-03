import os
import sqlite3
#########################################################################################################################################################################################
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(SCRIPT_DIR, "supersevens.db")
#########################################################################################################################################################################################
optionsad = """
1 - club edit
2 - team edit
3 - player edit
4 - match edit
5 - exit
"""
#########################################################################################################################################################################################
optionsus = """
1 - league table
2 - show all clubs
3 - show all teams
4 - show all players
5 - show all matches
6 - compare two clubs
7 - compare two teams
8 - compare two players
9 - compare two matches
10 - exit
"""
#########################################################################################################################################################################################
mainmenu = """
1 - admin functions
2 - user functions
3 - exit
"""
#########################################################################################################################################################################################
# all the players that play in a given match are stored here
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
#########################################################################################################################################################################################
# all the created clubs are stored in this table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
    """)
#########################################################################################################################################################################################
# all the created teams are stored in this table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER DEFAULT 0
        )
    """)
#########################################################################################################################################################################################
# all the created players are stored in this table
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
#########################################################################################################################################################################################
# all the created matches are stored in this table
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
#########################################################################################################################################################################################
# commits the changes to the file and closes it
    conn.commit()
    conn.close()
#########################################################################################################################################################################################
# saves time re wriiting over and over (the query is the statement and the paramater is the tuple variable to put in the placeholders)
def execute_query(query, params=()):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
#########################################################################################################################################################################################
# displays all of the tables contents depending on what table selected will explain at relevant lines
def display_all(table_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    print(f"\n=== Current {table_name.capitalize()} ===")
    if table_name == "clubs": # if the table name is clubs then print the contents of the clubs table and add the collumn cumulative points
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")
        else:
            print(f"{'ID':^6} | {'Club Name':^22} | {'Cumulative Points':^19}")
            print("-" * 55)
            for row in rows:
                print(f"{row[0]:^6} | {row[1]:^22} | {row[2]:^19}")
               
    elif table_name == "teams": # if the table name is teams then print the contents of the teams table and add the collumn cumulative points
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
        # Checks if the requested table is players then executes an aggregate SQL query (using agregate becase it takes multiple rows of data and puts them into a single summary value)
        # using LEFT JOINs to calculate and display each players total appearances 
        # and cumulative match points alongside their personal team and club details.
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
        rows = cursor.fetchall() # fetches all the rows of data generated and stores them in a list named rows
        if not rows:
            print("No records found.") # checks if rows is empty if it is prints an error message
        else:
            print(f"{'ID':^6} | {'Player Name':^26} | {'Number':^8} | {'Assigned Team':^22} | {'Assigned Club':^22} | {'Apps':^6} | {'Cumulative Pts':^17}") # if there is data in the list then it makes a table 26 characters wide and inside it hence the allignment
            print("-" * 134)#draws a row 134 lines long to seperate the data and make it look neat(this took a lot of fiddling)
            for row in rows: # checks each player to have a team if they do have a team good news if not then it prints a n.a next to them
                if row['team_name'] is not None:
                    t_name = row['team_name']
                else:
                    t_name = "N/A"
                if row['club_name'] is not None: # same premise but for the clubs of players instead
                    c_name = row['club_name']
                else:
                    c_name = "N/A"
                   
                apps = row['total_appearances'] #extracts the count of how many appearances they have had and displays it 
                display_pts = int(row['total_player_points'])#same premise same math different variables outputted in the print statement below
                print(f"{row['id']:^6} | {row['player_name']:^26} | {row['number']:^8} | {t_name:^22} | {c_name:^22} | {apps:^6} | {display_pts:^17}")
#########################################################################################################################################################################################      
    elif table_name == "matches":
        conn.row_factory = sqlite3.Row # i had trouble with the returns of the table so i looked into turning the peices into objects and accessing the collumns directly which is way easier
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
        """)#talbe uses join statements to link the ids in matches to clubs and teams the away and home js makes everything easier to read when editing program
        rows = cursor.fetchall()
        if not rows:
            print("No records found.")#instead of checking if everything is in there we just check that something isnt then assume that its all there
        else:
            print(f"{'ID':^5} | {'Date':^12} | {'Home Club':^16} | {'Home Team':^23} | {'H-Score':^7} | {'A-Score':^7} | {'Away Team':^23} | {'Away Club':^16}")#this prints all my headers and everything should be in the middle of them
            print("-" * 143)#this should match the end of the last word and make it all look neat
            for row in rows:
                print(f"{row['id']:^5} | {row['match_date']:^12} | {row['home_club']:^16} | {row['home_team']:^23} | {row['home_score']:^7} | {row['away_score']:^7} | {row['away_team']:^23} | {row['away_club']:^16}")            
    conn.close()
    print("=" * 25)
#########################################################################################################################################################################################
def addclub():#this adds clubs to the clubs table it dosent have a points so everything is calculated this prevents errors and more accurate results
    print("\n--- Clubs ---")
    club_name = input("input club name: ")
    execute_query("INSERT INTO clubs (name) VALUES (?)", (club_name,))
    print(f"Club '{club_name}' added successfully.")
#########################################################################################################################################################################################
def editclub():
    display_all("clubs")
    club_ID = int(input("input club id: "))
    new_name = input("input new club name: ")
    execute_query("UPDATE clubs SET name = ? WHERE id = ?", (new_name, club_ID))
    print("Club updated successfully.")
#########################################################################################################################################################################################
def removeclub():
    display_all("clubs")
    club_ID = int(input("input club id: "))
    execute_query("DELETE FROM clubs WHERE id = ?", (club_ID,))
    execute_query("DELETE FROM players WHERE club_id = ?", (club_ID,))
    print("Club and its registered players removed successfully.")
#########################################################################################################################################################################################
def listclub():
    display_all("clubs")
#########################################################################################################################################################################################
def clubedit():
    while True:
        print("""
1 - add
2 - edit
3 - remove
4 - list
5 - back""")
        choice = int(input("input an option: "))
        if choice == 1:
            addclub()
        elif choice == 2:
            editclub()
        elif choice == 3:
            removeclub()
        elif choice == 4:
            listclub()
        elif choice == 5:
            break
        else:
            print("Invalid alternative choice selected.")
#########################################################################################################################################################################################
def addteam():
    print("\n--- Teams ---")
    team_name = input("input team name: ")
    execute_query("INSERT INTO teams (name) VALUES (?)", (team_name,))
    print(f"Team '{team_name}' added successfully.")
#########################################################################################################################################################################################
def editteam():
    display_all("teams")
    team_ID = int(input("input team id: "))
    new_name = input("input new team name: ")
    execute_query("UPDATE teams SET name = ? WHERE id = ?", (new_name, team_ID))
    print("Team updated successfully.")
#########################################################################################################################################################################################
def removeteam():
    display_all("teams")
    team_ID = int(input("input team id: "))
    execute_query("DELETE FROM teams WHERE id = ?", (team_ID,))
    execute_query("DELETE FROM players WHERE team_id = ?", (team_ID,))
    print("Team and its registered players removed successfully.")
#########################################################################################################################################################################################
def listteams():
    display_all("teams")
#########################################################################################################################################################################################
def teamedit():
    while True:
        print("""
1 - add
2 - edit
3 - remove
4 - list
5 - back""")
        choice = int(input("input an option: "))
        if choice == 1:
            addteam()
        elif choice == 2:
            editteam()
        elif choice == 3:
            removeteam()
        elif choice == 4:
            listteams()
        elif choice == 5:
            break
        else:
            print("Invalid alternative choice selected.")
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
def removeplayer():
    display_all("players")
    player_ID = int(input("input player id: "))
    execute_query("DELETE FROM players WHERE id = ?", (player_ID,))
    execute_query("DELETE FROM match_players WHERE player_id = ?", (player_ID,))
    print("Player removed successfully.")
#########################################################################################################################################################################################
def listplayers():
    display_all("players")
#########################################################################################################################################################################################
def playeredit():
    while True:
        print("""
1 - add
2 - edit
3 - remove
4 - list
5 - back""")
        choice = int(input("input an option: "))
        if choice == 1:
            addplayer()
        elif choice == 2:
            editplayer()
        elif choice == 3:
            removeplayer()
        elif choice == 4:
            listplayers()
        elif choice == 5:
            break
        else:
            print("Invalid alternative choice selected.")
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
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
#########################################################################################################################################################################################
def listmatch():
    display_all("matches")
#########################################################################################################################################################################################
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
    print(f"Subtracted {away_score} pts from Club {away_club}/Team {away_team}")
#########################################################################################################################################################################################
def matchedit():
    while True:
        print("""
1 - add
2 - edit
3 - remove
4 - list
5 - view match roster
6 - back""")
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
        elif choice == 6:
            break
        else:
            print("Invalid alternative choice selected.")
#########################################################################################################################################################################################
def showAllClubsUser():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    GAME_MINUTES = 45.0
    cursor.execute("SELECT id, name, points FROM clubs ORDER BY id ASC")
    clubs = cursor.fetchall()
   
    if not clubs:
        print("\n" + "=" * 25 + "\nNo records found.\n" + "=" * 25)
        conn.close()
        return

    max_name_len = 15
    for club in clubs:
        if len(club[1]) > max_name_len:
            max_name_len = len(club[1])
           
    processed_clubs = []
    for club in clubs:
        club_id, club_name, points = club
        cursor.execute("SELECT id FROM teams WHERE name LIKE ?", (f"%{club_name}%",))
        team_ids = [row[0] for row in cursor.fetchall()]
       
        games_played = 0
        if team_ids:
            placeholders = ",".join("?" for _ in team_ids)
            cursor.execute(f"""
                SELECT COUNT(id) FROM matches
                WHERE home_team_id IN ({placeholders}) OR away_team_id IN ({placeholders})
            """, team_ids + team_ids)
            games_played = cursor.fetchone()[0]
       
        avg_ppg = points / games_played if games_played > 0 else 0.0
        avg_ppm = avg_ppg / GAME_MINUTES if avg_ppg > 0 else 0.0
        processed_clubs.append((club_id, club_name, points, avg_ppg, avg_ppm))
    conn.close()

    total_width = max_name_len + 52
    print("\n" + "=" * total_width)
    print(f"{'ALL REGISTERED CLUBS & AGGREGATE EFFICIENCY':^{total_width}}")
    print("=" * total_width)
    print(f"{'ID':^6} | {f'Club Name':<{max_name_len}} | {'Ladder Pts':^12} | {'Avg PPG':^12} | {'Avg PPM':^12}")
    print("-" * total_width)
    for c_id, name, pts, ppg, ppm in processed_clubs:
        print(f"{c_id:^6} | {name:<{max_name_len}} | {pts:^12} | {ppg:^12.2f} | {ppm:^12.2f}")
    print("=" * total_width)
#########################################################################################################################################################################################
def showAllTeamsUser():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    GAME_MINUTES = 45.0
    cursor.execute("""
        SELECT t.id, t.name, t.points, COUNT(m.id) AS games_played
        FROM teams t
        LEFT JOIN matches m ON t.id = m.home_team_id OR t.id = m.away_team_id
        GROUP BY t.id
        ORDER BY t.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\n" + "=" * 25 + "\nNo records found.\n" + "=" * 25)
        return

    max_name_len = 15  
    for row in rows:
        if len(row[1]) > max_name_len:
            max_name_len = len(row[1])

    total_width = max_name_len + 52
    print("\n" + "=" * total_width)
    print(f"{'ALL REGISTERED TEAMS & PERFORMANCE EFFICIENCY':^{total_width}}")
    print("=" * total_width)
    print(f"{'ID':^6} | {f'Team Squad Name':<{max_name_len}} | {'Ladder Pts':^12} | {'Avg PPG':^12} | {'Avg PPM':^12}")
    print("-" * total_width)
    for team_id, team_name, points, games_played in rows:
        avg_ppg = points / games_played if games_played > 0 else 0.0
        avg_ppm = avg_ppg / GAME_MINUTES if avg_ppg > 0 else 0.0
        print(f"{team_id:^6} | {team_name:<{max_name_len}} | {points:^12} | {avg_ppg:^12.2f} | {avg_ppm:^12.2f}")
    print("=" * total_width)
#########################################################################################################################################################################################
def showAllPlayersUser():
    display_all("players")
#########################################################################################################################################################################################
def showAllMatchesUser():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.match_date, hc.name AS home_club, ht.name AS home_team,
               m.home_score, m.away_score, at.name AS away_team, ac.name AS away_club
        FROM matches m
        JOIN clubs hc ON m.home_club_id = hc.id
        JOIN clubs ac ON m.away_club_id = ac.id
        JOIN teams ht ON m.home_team_id = ht.id
        JOIN teams at ON m.away_team_id = at.id
        ORDER BY m.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\n" + "=" * 25 + "\nNo records found.\n" + "=" * 25)
        return

    GAME_MINUTES = 45.0
    processed_rows = []
    max_home_len = 15  
    max_away_len = 15  

    for row in rows:
        home_display = f"{row['home_club']} {row['home_team']}"
        away_display = f"{row['away_club']} {row['away_team']}"
        if len(home_display) > max_home_len:
            max_home_len = len(home_display)
        if len(away_display) > max_away_len:
            max_away_len = len(away_display)
           
        processed_rows.append({
            "id": row['id'], "date": row['match_date'], "home": home_display,
            "h_score": row['home_score'], "a_score": row['away_score'], "away": away_display,
            "h_ppm": row['home_score'] / GAME_MINUTES, "a_ppm": row['away_score'] / GAME_MINUTES,
            "t_ppm": (row['home_score'] + row['away_score']) / GAME_MINUTES
        })

    total_table_width = max_home_len + max_away_len + 64
    print("\n" + "=" * total_table_width)
    print(f"{'MATCH HISTORY LOG & EFFICIENCY (PPM)':^{total_table_width}}")
    print("=" * total_table_width)
    print(f"{'ID':^4} | {'Date':^10} | {f'Home Squad':<{max_home_len}} | {'H-Pts':^5} | {'A-Pts':^5} | {f'Away Squad':<{max_away_len}} | {'H-PPM':^6} | {'A-PPM':^6} | {'Total PPM':^9}")
    print("-" * total_table_width)
    for r in processed_rows:
        print(f"{r['id']:^4} | {r['date']:^10} | {r['home']:<{max_home_len}} | {r['h_score']:^5} | {r['a_score']:^5} | {r['away']:<{max_away_len}} | {r['h_ppm']:^6.2f} | {r['a_ppm']:^6.2f} | {r['t_ppm']:^9.2f}")
    print("=" * total_table_width)
#########################################################################################################################################################################################
def customLeagueStandingsReport():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    GAME_MINUTES = 45.0
    cursor.execute("""
        SELECT t.name, t.points,
            TOTAL(CASE WHEN (m.home_team_id = t.id AND m.home_score > m.away_score) OR (m.away_team_id = t.id AND m.away_score > m.home_score) THEN 1 ELSE 0 END) AS wins,
            TOTAL(CASE WHEN (m.home_team_id = t.id AND m.home_score < m.away_score) OR (m.away_team_id = t.id AND m.away_score < m.home_score) THEN 1 ELSE 0 END) AS losses,
            TOTAL(CASE WHEN (m.home_team_id = t.id OR m.away_team_id = t.id) AND m.home_score = m.away_score THEN 1 ELSE 0 END) AS draws,
            COUNT(m.id) AS games_played
        FROM teams t
        LEFT JOIN matches m ON t.id = m.home_team_id OR t.id = m.away_team_id
        GROUP BY t.id
        ORDER BY t.points DESC, wins DESC, t.name ASC
    """)
    teams = cursor.fetchall()
    conn.close()

    if not teams:
        print("\n" + "=" * 25 + "\nNo records found.\n" + "=" * 25)
        return

    max_name_len = 15  
    for team in teams:
        if len(team[0]) > max_name_len:
            max_name_len = len(team[0])

    total_width = max_name_len + 62
    print("\n" + "=" * total_width)
    print(f"{'COMPREHENSIVE LEAGUE STANDINGS & EFFICIENCY RATINGS':^{total_width}}")
    print("=" * total_width)
    print(f"{'Rank':^5} | {f'Team Squad Name':<{max_name_len}} | {'Pts':^6} | {'Wins':^5} | {'Losses':^6} | {'Draws':^5} | {'Avg PPG':^9} | {'Avg PPM':^9}")
    print("-" * total_width)
    for rank, team in enumerate(teams, start=1):
        name, pts, wins, losses, draws, games_played = team
        avg_ppg = pts / games_played if games_played > 0 else 0.0
        avg_ppm = avg_ppg / GAME_MINUTES if avg_ppg > 0 else 0.0
        print(f"{rank:^5} | {name:<{max_name_len}} | {pts:^6} | {int(wins):^5} | {int(losses):^6} | {int(draws):^5} | {avg_ppg:^9.2f} | {avg_ppm:^9.2f}")
    print("=" * total_width)
#########################################################################################################################################################################################
def calculateTeamMetrics(cursor, team_id):
    cursor.execute("""
        SELECT home_team_id, away_team_id, home_score, away_score
        FROM matches
        WHERE home_team_id = ? OR away_team_id = ?
    """, (team_id, team_id))
    matches = cursor.fetchall()
   
    w, l, d, scored = 0, 0, 0, 0
    for m in matches:
        if m[0] == team_id:
            scored += m[2]
            if m[2] > m[3]: w += 1
            elif m[2] < m[3]: l += 1
            else: d += 1
        else:
            scored += m[3]
            if m[3] > m[2]: w += 1
            elif m[3] < m[2]: l += 1
            else: d += 1
           
    avg_ppg = scored / len(matches) if matches else 0.0
    return w, l, d, len(matches), avg_ppg
#########################################################################################################################################################################################
def compareClubsMatrix():
    display_all("clubs")
    try:
        c1 = int(input("\nEnter First Club ID: "))
        c2 = int(input("Enter Second Club ID: "))
        if c1 == c2:
            print("Selection error: Cannot process identical variables.")
            return

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        club_data = {}
        for cid in (c1, c2):
            cursor.execute("SELECT name, points FROM clubs WHERE id = ?", (cid,))
            res = cursor.fetchone()
            if not res:
                print("Error: Target database object not found.")
                conn.close()
                return
           
            cursor.execute("SELECT id FROM teams WHERE name LIKE ?", (f"%{res[0]}%",))
            t_ids = [r[0] for r in cursor.fetchall()]
           
            c_wins, c_losses, c_draws, c_games, c_scored = 0, 0, 0, 0, 0
            for tid in t_ids:
                w, l, d, games, avg_ppg = calculateTeamMetrics(cursor, tid)
                c_wins += w; c_losses += l; c_draws += d; c_games += games
                c_scored += (avg_ppg * games)
               
            club_data[cid] = {
                "name": res[0], "pts": res[1], "w": c_wins, "l": c_losses,
                "d": c_draws, "avg": c_scored / c_games if c_games > 0 else 0.0
            }
        conn.close()

        d1, d2 = club_data[c1], club_data[c2]
        col0_width = len("Average Points/Game")
        col1_width = max(17, len(d1['name']))
        col2_width = max(17, len(d2['name']))
        total_matrix_width = col0_width + col1_width + col2_width + 6

        print("\n" + "=" * total_matrix_width)
        print(f"{'ANALYTICAL METRIC COMPARISON MATRIX (CLUBS)':^{total_matrix_width}}")
        print("=" * total_matrix_width)
        print(f"{'Performance Indicator':<{col0_width}} | {d1['name']:^{col1_width}} | {d2['name']:^{col2_width}}")
        print("-" * total_matrix_width)
        print(f"{'Total Ladder Points':<{col0_width}} | {d1['pts']:^{col1_width}} | {d2['pts']:^{col2_width}}")
        print(f"{'Aggregated Wins':<{col0_width}} | {d1['w']:^{col1_width}} | {d2['w']:^{col2_width}}")
        print(f"{'Aggregated Losses':<{col0_width}} | {d1['l']:^{col1_width}} | {d2['l']:^{col2_width}}")
        print(f"{'Aggregated Draws':<{col0_width}} | {d1['d']:^{col1_width}} | {d2['d']:^{col2_width}}")
        print(f"{'Average Points/Game':<{col0_width}} | {d1['avg']:^{col1_width}.2f} | {d2['avg']:^{col2_width}.2f}")
        print("=" * total_matrix_width)
    except ValueError:
        print("Invalid Selection Format.")
#########################################################################################################################################################################################
def compareTeamsMatrix():
    display_all("teams")
    try:
        t1 = int(input("\nEnter First Team ID: "))
        t2 = int(input("Enter Second Team ID: "))
        if t1 == t2:
            print("Selection error: Cannot process identical variables.")
            return

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        team_data = {}
        for tid in (t1, t2):
            cursor.execute("SELECT name, points FROM teams WHERE id = ?", (tid,))
            res = cursor.fetchone()
            if not res:
                print("Error: Target database object not found.")
                conn.close()
                return
            w, l, d, games, avg_ppg = calculateTeamMetrics(cursor, tid)
            team_data[tid] = {"name": res[0], "pts": res[1], "w": w, "l": l, "d": d, "avg": avg_ppg}
        conn.close()

        d1, d2 = team_data[t1], team_data[t2]
        col0_width = len("Average Points/Game")
        col1_width = max(17, len(d1['name']))
        col2_width = max(17, len(d2['name']))
        total_matrix_width = col0_width + col1_width + col2_width + 6

        print("\n" + "=" * total_matrix_width)
        print(f"{'ANALYTICAL METRIC COMPARISON MATRIX (TEAMS)':^{total_matrix_width}}")
        print("=" * total_matrix_width)
        print(f"{'Performance Indicator':<{col0_width}} | {d1['name']:^{col1_width}} | {d2['name']:^{col2_width}}")
        print("-" * total_matrix_width)
        print(f"{'Total Ladder Points':<{col0_width}} | {d1['pts']:^{col1_width}} | {d2['pts']:^{col2_width}}")
        print(f"{'Recorded Wins':<{col0_width}} | {d1['w']:^{col1_width}} | {d2['w']:^{col2_width}}")
        print(f"{'Recorded Losses':<{col0_width}} | {d1['l']:^{col1_width}} | {d2['l']:^{col2_width}}")
        print(f"{'Recorded Draws':<{col0_width}} | {d1['d']:^{col1_width}} | {d2['d']:^{col2_width}}")
        print(f"{'Average Points/Game':<{col0_width}} | {d1['avg']:^{col1_width}.2f} | {d2['avg']:^{col2_width}.2f}")
        print("=" * total_matrix_width)
    except ValueError:
        print("Invalid Selection Format.")
#########################################################################################################################################################################################
def comparePlayersMatrix():
    display_all("players")
    try:
        p1 = int(input("\nEnter First Player ID: "))
        p2 = int(input("Enter Second Player ID: "))
        if p1 == p2:
            print("Selection error: Cannot process identical variables.")
            return

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        p_data = {}
        for pid in (p1, p2):
            cursor.execute("SELECT name, team_id FROM players WHERE id = ?", (pid,))
            base = cursor.fetchone()
            if not base:
                print("Error: Target database object not found.")
                conn.close()
                return
           
            p_name, team_id = base[0], base[1]
            cursor.execute("SELECT COUNT(match_id), TOTAL(points) FROM match_players WHERE player_id = ?", (pid,))
            m_stat = cursor.fetchone()
            app = m_stat[0] if m_stat else 0
            pts = m_stat[1] if m_stat else 0.0
            avg_ppg = pts / app if app > 0 else 0.0

            w, l, d = 0, 0, 0
            if team_id:
                w, l, d, _, _ = calculateTeamMetrics(cursor, team_id)

            p_data[pid] = {"name": p_name, "app": app, "w": w, "l": l, "d": d, "pts": pts, "avg": avg_ppg}
        conn.close()

        d1, d2 = p_data[p1], p_data[p2]
        col0_width = len("Squad Wins While Registered")
        col1_width = max(17, len(d1['name']))
        col2_width = max(17, len(d2['name']))
        total_matrix_width = col0_width + col1_width + col2_width + 6

        print("\n" + "=" * total_matrix_width)
        print(f"{'COMPREHENSIVE ATHLETE PROFILE MATRIX':^{total_matrix_width}}")
        print("=" * total_matrix_width)
        print(f"{'Analytical Dimension':<{col0_width}} | {d1['name']:^{col1_width}} | {d2['name']:^{col2_width}}")
        print("-" * total_matrix_width)
        print(f"{'Total Appearances (APP)':<{col0_width}} | {d1['app']:^{col1_width}} | {d2['app']:^{col2_width}}")
        print(f"{'Squad Wins While Registered':<{col0_width}} | {d1['w']:^{col1_width}} | {d2['w']:^{col2_width}}")
        print(f"{'Squad Losses While Reg.':<{col0_width}} | {d1['l']:^{col1_width}} | {d2['l']:^{col2_width}}")
        print(f"{'Squad Draws While Reg.':<{col0_width}} | {d1['d']:^{col1_width}} | {d2['d']:^{col2_width}}")
        print(f"{'Absolute Points Logged':<{col0_width}} | {int(d1['pts']):^{col1_width}} | {int(d2['pts']):^{col2_width}}")
        print(f"{'Individual Points / Game':<{col0_width}} | {d1['avg']:^{col1_width}.2f} | {d2['avg']:^{col2_width}.2f}")
        print("=" * total_matrix_width)
    except ValueError:
        print("Invalid Selection Format.")
#########################################################################################################################################################################################
def compareMatchesMatrix():
    display_all("matches")
    try:
        m1 = int(input("\nEnter First Match ID: "))
        m2 = int(input("Enter Second Match ID: "))
        if m1 == m2:
            print("Selection error: Cannot process identical variables.")
            return

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        m_data = {}
        GAME_MINUTES = 45.0

        for mid in (m1, m2):
            cursor.execute("SELECT id, home_score, away_score FROM matches WHERE id = ?", (mid,))
            res = cursor.fetchone()
            if not res:
                print("Error: Target database object not found.")
                conn.close()
                return
           
            h_pts, a_pts = res[1], res[2]
            difference = abs(h_pts - a_pts)
           
            m_data[mid] = {
                "label": f"Match ID {res[0]}", "h_pts": h_pts, "a_pts": a_pts, "diff": difference,
                "hppm": h_pts / GAME_MINUTES, "appm": a_pts / GAME_MINUTES, "tppm": (h_pts + a_pts) / GAME_MINUTES
            }
        conn.close()

        d1, d2 = m_data[m1], m_data[m2]
        col0_width = len("Total Match PPM")
        col1_width = max(17, len(d1['label']))
        col2_width = max(17, len(d2['label']))
        total_matrix_width = col0_width + col1_width + col2_width + 6

        print("\n" + "=" * total_matrix_width)
        print(f"{'SIMPLIFIED MATCH EFFICIENCY COMPARISON':^{total_matrix_width}}")
        print("=" * total_matrix_width)
        print(f"{'Efficiency Metric':<{col0_width}} | {d1['label']:^{col1_width}} | {d2['label']:^{col2_width}}")
        print("-" * total_matrix_width)
        print(f"{'Home Points':<{col0_width}} | {int(d1['h_pts']):^{col1_width}} | {int(d2['h_pts']):^{col2_width}}")
        print(f"{'Away Points':<{col0_width}} | {int(d1['a_pts']):^{col1_width}} | {int(d2['a_pts']):^{col2_width}}")
        print(f"{'Score Difference':<{col0_width}} | {int(d1['diff']):^{col1_width}} | {int(d2['diff']):^{col2_width}}")
        print("-" * total_matrix_width)
        print(f"{'Home PPM':<{col0_width}} | {d1['hppm']:^{col1_width}.2f} | {d2['hppm']:^{col2_width}.2f}")
        print(f"{'Away PPM':<{col0_width}} | {d1['appm']:^{col1_width}.2f} | {d2['appm']:^{col2_width}.2f}")
        print(f"{'Total Match PPM':<{col0_width}} | {d1['tppm']:^{col1_width}.2f} | {d2['tppm']:^{col2_width}.2f}")
        print("=" * total_matrix_width)
    except ValueError:
        print("Invalid Selection Format.")
#########################################################################################################################################################################################
def admin_menu():
    while True:
        print("\n=== ADMIN OPERATIONS CONTROLLER ===")
        print(optionsad)
        try:
            choice = int(input("Select configurations (1-5): "))
            if choice == 1:
                clubedit()
            elif choice == 2:
                teamedit()
            elif choice == 3:
                playeredit()
            elif choice == 4:
                matchedit()
            elif choice == 5:
                break
            else:
                print("Invalid alternative selection.")
        except ValueError:
            print("Numeric data inputs only.")
#########################################################################################################################################################################################
def user_menu():
    while True:
        print("\n=== USER ANALYTICAL SYSTEM ===")
        print(optionsus)
        try:
            choice = int(input("Select report matrix (1-10): "))
            if choice == 1:
                customLeagueStandingsReport()
            elif choice == 2:
                showAllClubsUser()
            elif choice == 3:
                showAllTeamsUser()
            elif choice == 4:
                showAllPlayersUser()
            elif choice == 5:
                showAllMatchesUser()
            elif choice == 6:
                compareClubsMatrix()
            elif choice == 7:
                compareTeamsMatrix()
            elif choice == 8:
                comparePlayersMatrix()
            elif choice == 9:
                compareMatchesMatrix()
            elif choice == 10:
                break
            else:
                print("Invalid alternative selection.")
        except ValueError:
            print("Numeric data inputs only.")
#########################################################################################################################################################################################
def main():
    init_db()
    while True:
        print("\n=== SUPER SEVENS CENTRAL APPLICATION INTEGRATION ===")
        print(mainmenu)
        try:
            choice = int(input("Route selection (1-3): "))
            if choice == 1:
                admin_menu()
            elif choice == 2:
                user_menu()
            elif choice == 3:
                print("\nClosing analytical terminal pipelines. System offline. Goodbye!")
                break
            else:
                print("Invalid alternative entry.")
        except ValueError:
            print("Numeric entry criteria only.")
#########################################################################################################################################################################################
if __name__ == "__main__":
    main()