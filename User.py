import os
import sqlite3

# Dynamically find the absolute path of the directory where this script resides
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(SCRIPT_DIR, "supersevens.db")



def showAllClubs():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
   
    GAME_MINUTES = 45.0
    cursor.execute("SELECT id, name, points FROM clubs ORDER BY id ASC")
    clubs = cursor.fetchall()
   
    if not clubs:
        print("\n" + "=" * 25)
        print("error")
        print("=" * 25)
        conn.close()
        return


    processed_clubs = []
    max_name_len = 9  


    for club in clubs:
        club_id, club_name, points = club
        if len(club_name) > max_name_len:
            max_name_len = len(club_name)
           
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




def showAllTeams():
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
        print("\n" + "=" * 25)
        print("error")
        print("=" * 25)
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




def showAllPlayers():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.number, t.name AS squad_name,
               COUNT(mp.match_id) AS appearances, TOTAL(mp.points) AS total_points
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.id
        LEFT JOIN match_players mp ON p.id = mp.player_id
        GROUP BY p.id
        ORDER BY p.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()


    if not rows:
        print("\n" + "=" * 27)
        print("error")
        print("=" * 27)
        return


    max_pname_len = 11  
    max_sname_len = 19  


    for row in rows:
        p_name = row[1]
        s_name = row[3] if row[3] else "Unassigned"
        if len(p_name) > max_pname_len:
            max_pname_len = len(p_name)
        if len(s_name) > max_sname_len:
            max_sname_len = len(s_name)


    total_width = max_pname_len + max_sname_len + 31


    print("\n" + "=" * total_width)
    print(f"{'ALL SQUAD PLAYER DIRECTORY & EFFICIENCY RATINGS':^{total_width}}")
    print("=" * total_width)
    print(f"{'ID':^6} | {f'Player Name':<{max_pname_len}} | {'No.':^5} | {f'Assigned Team Squad':<{max_sname_len}} | {'Avg PPG':^10}")
    print("-" * total_width)
    for row in rows:
        p_id, p_name, p_num, squad, apps, total_pts = row
        squad_display = squad if squad else "Unassigned"
        avg_ppg = total_pts / apps if apps > 0 else 0.0
        print(f"{p_id:^6} | {p_name:<{max_pname_len}} | {p_num:^5} | {squad_display:<{max_sname_len}} | {avg_ppg:^10.2f}")
    print("=" * total_width)




def showAllMatches():
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
        print("\n" + "=" * 36)
        print("error")
        print("=" * 36)
        return


    GAME_MINUTES = 45.0
    processed_rows = []
    max_home_len = 10  
    max_away_len = 10  


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
        print("\n" + "=" * 25)
        print("error")
        print("=" * 25)
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




def compareClubsMatrix():
    showAllClubs()
    try:
        c1 = int(input("\nEnter First Club ID: "))
        c2 = int(input("Enter Second Club ID: "))
        if c1 == c2:
            print("error")
            return


        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()


        club_data = {}
        for cid in (c1, c2):
            cursor.execute("SELECT name, points FROM clubs WHERE id = ?", (cid,))
            res = cursor.fetchone()
            if not res:
                print("error")
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
        print("error")




def compareTeamsMatrix():
    showAllTeams()
    try:
        t1 = int(input("\nEnter First Team ID: "))
        t2 = int(input("Enter Second Team ID: "))
        if t1 == t2:
            print("error")
            return


        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()


        team_data = {}
        for tid in (t1, t2):
            cursor.execute("SELECT name, points FROM teams WHERE id = ?", (tid,))
            res = cursor.fetchone()
            if not res:
                print("error")
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
        print("error")




def comparePlayersMatrix():
    showAllPlayers()
    try:
        p1 = int(input("\nEnter First Player ID: "))
        p2 = int(input("Enter Second Player ID: "))
        if p1 == p2:
            print("error")
            return


        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()


        p_data = {}
        for pid in (p1, p2):
            cursor.execute("SELECT name, team_id FROM players WHERE id = ?", (pid,))
            base = cursor.fetchone()
            if not base:
                print("error")
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
        print("error")




def compareMatchesMatrix():
    showAllMatches()
    try:
        m1 = int(input("\nEnter First Match ID: "))
        m2 = int(input("Enter Second Match ID: "))
        if m1 == m2:
            print("error")
            return


        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()


        m_data = {}
        GAME_MINUTES = 45.0


        for mid in (m1, m2):
            cursor.execute("SELECT id, home_score, away_score FROM matches WHERE id = ?", (mid,))
            res = cursor.fetchone()
            if not res:
                print("error")
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
        print("error")




def main():
    while True:
        print("""
=== SUPER SEVENS MULTI-ANALYTICS DASHBOARD ===
1  - View Expanded League Table (Teams, Points, Wins, Losses, Draws)
2  - Directory: Show All Clubs (Admin View)
3  - Directory: Show All Teams (Admin View)
4  - Directory: Show All Players (Admin View)
5  - Directory: Show All Matches (Admin View)
6  - Comparative Matrix: Two Clubs (W/L/D & PPG)
7  - Comparative Matrix: Two Teams (W/L/D & PPG)
8  - Comparative Matrix: Two Players Profile (APP, W/L/D, PPG)
9  - Comparative Matrix: Two Matches Profile (PPM Efficiency Analysis)
10 - Exit Analytics Module""")


        try:
            choice = int(input("\nSelect an analytical reporting matrix (1-10): "))
            if choice == 1:
                customLeagueStandingsReport()
            elif choice == 2:
                showAllClubs()
            elif choice == 3:
                showAllTeams()
            elif choice == 4:
                showAllPlayers()
            elif choice == 5:
                showAllMatches()
            elif choice == 6:
                compareClubsMatrix()
            elif choice == 7:
                compareTeamsMatrix()
            elif choice == 8:
                comparePlayersMatrix()
            elif choice == 9:
                compareMatchesMatrix()
            elif choice == 10:
                print("Closing analytical terminal. Terminal pipeline offline. Goodbye!")
                break
            else:
                print("error")
        except ValueError:
            print("error")




if __name__ == "__main__":
    main()

