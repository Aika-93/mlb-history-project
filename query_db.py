"""
MLB Database Query Program
Allows users to query the MLB SQLite database from the command line:

1. View All-Star Games by year
2. View award winners (MVP, CY Young, Rookie of the year) by team.
3. View All-Star Games with MVP winners by year.

Handles user input, joins tables, and displays results with error handling.
"""

import sqlite3
import pandas as pd

#Path to the SQLite database
DATABASE = "mlb_history.db"

# =====================================================================================================================================
# SHOW ALL-STAR GAMES FOR A SPECIFIC YEAR
# =====================================================================================================================================
def show_all_star_by_year():
    year = input("Enter year: ")

    query = """
    SELECT *
    FROM all_star_game
    WHERE Year = ?
    """
    try:
        with sqlite3.connect(DATABASE) as conn:
            df = pd.read_sql(query, conn, params=(year,))
            if df.empty:
                print("No games found for that year.")
            else:
                print(df)
    except Exception as e:
        print("Error: ", e)

# =========================================================================================================================================
# SHOW ALL AWARD WINNERS FOR A SPECIFIC TEAM
# Combines MVP, CY Young, and Rookie of the Year
# ========================================================================================================================================

def show_awards_by_team():
    team = input("Enter team name: ")
    team_param = f"%{team}%"

    query = """
    SELECT 'MVP' AS Award, Year, Name, Team
    FROM all_star_mvp_award
    WHERE Team LIKE ?
    
    UNION ALL
    
    SELECT 'CY YOUNG' AS Award, Year, Name, Team
    FROM cy_young_award
    WHERE Team LIKE ?
    
    UNION ALL
    
    SELECT "Rookie of the Year" AS Award, Year, Name, Team
    FROM rookie_of_the_year_award
    WHERE Team LIKE ?
    """
    try:
        with sqlite3.connect(DATABASE) as conn:
            df = pd.read_sql(query, conn, params=(team_param, team_param, team_param))
            if df.empty:
                print("No awards found for that team.")
            else:
                print(df)
    except Exception as e:
        print("Error: ", e)

# =======================================================================================================================================
# SHOW ALL-STAR GAMES ALONG WITH MVP WINNER FOR A SPECIFIC YEAR
# Uses a JOIN between all_star_game and all_star_mvp_award
# ========================================================================================================================================

def show_all_star_with_mvp():
    year = input("Enter year to filter All-Star games with MVP: ")

    query = """
    SELECT
        g.Year,
        g.AL,
        g.NL,
        m.Name AS MVP_Name,
        m.Team
    FROM all_star_game g
    JOIN all_star_mvp_award m
        ON g.Year = m.Year
    WHERE g.Year = ?
    ORDER BY g.Year
    """
    try:
        with sqlite3.connect(DATABASE) as conn:
            df = pd.read_sql(query, conn, params=(year,))
            if df.empty:
                print(f"No All-Star games with MVP found for year {year}.")
            else:
                print(df)
    except Exception as e:
        print("Error: ", e)

# ====================================================================================================================================
# MAIN PROGRAM LOOP
# Displays menu and calls appropriate functions based on user choice
# ====================================================================================================================================

def main():
    while True:
        print("\n-----MLB DATABASE QUERY PROGRAM-----")
        print("1 - Show All-Star Games by Year")
        print("2 - Show Awards by Team")
        print("3 - Show All-Star Games with MVP (JOIN)")
        print("4 Exit")

        choice = input("Select an option: ")

        if choice == "1":
            show_all_star_by_year()
        elif choice == "2":
            show_awards_by_team()
        elif choice == "3":
            show_all_star_with_mvp()
        elif choice == "4":
            print("Goodbye")
            break
        else:
            print("Invalid option. Please try again.")

#Run the program
if __name__ == "__main__":
    main()