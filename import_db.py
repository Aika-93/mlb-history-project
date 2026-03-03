"""
MLB Data Import and Cleaning

This script loads raw MLB data, performs initial cleaning and necessary transformations, 
and stores the processed data into a SQLite database for further analysis and visualization.

"""

import sqlite3
import pandas as pd


# =============================================================================================
# PART 1: DATABASE IMPORT
# =============================================================================================

#List of CSV files
csv_files = {
    "all_star_game": "data/all_star_game.csv",
    "all_star_mvp_award": "data/awards/all_star_mvp_award.csv",
    "cy_young_award": "data/awards/cy_young_award.csv",
    "rookie_of_the_year_award": "data/awards/rookie_of_the_year_award.csv",
    "managers": "data/managers.csv"
}

with sqlite3.connect("mlb_history.db") as conn:

    for table_name, file_path in csv_files.items():
        try: 
            #Load CSV file into a Pandas DataFrame
            df = pd.read_csv(file_path)
        
            #Write DataFrame to SQLite
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        
            print(f"{table_name} imported successfully")
        
        except FileNotFoundError:
            print(f"File not found: {file_path}")

        except Exception as e:
            print(f"Unexpected error for {file_path}: {e}")

print("\nImport process finished")

# ===============================================================================================
# PART 2: LOAD DATA INTO PANDAS
# ===============================================================================================

with sqlite3.connect("mlb_history.db") as conn:
    all_star_df = pd.read_sql("SELECT * FROM all_star_game", conn)
    mvp_df = pd.read_sql("SELECT * FROM all_star_mvp_award", conn)
    cy_young_df = pd.read_sql("SELECT * FROM cy_young_award", conn)
    rookie_df = pd.read_sql("SELECT * FROM rookie_of_the_year_award", conn)
    managers_df = pd.read_sql("SELECT * FROM managers", conn)

print("Data loaded from SQLite successfully")

# ==============================================================================================
# PART 3: CLEANING - ALL-STAR DATA
# ==============================================================================================

def clean_all_star(all_star_df):
    """
    Clean All_Star Game dataset:
    - Remove duplicates
    - Convert date and numeric columns
    - Handle missing values
    - Create analytical features (Year, Total_Runs)
    """
    print("BEFORE CLEANING")
    print("Shape:", all_star_df.shape)
    print("\n Missing values:\n",all_star_df.isnull().sum())
    print("\nDuplicate rows:", all_star_df.duplicated().sum())
    print("Sample data:")
    print(all_star_df.head())

    #Remove duplicate rows
    all_star_df = all_star_df.drop_duplicates()

    #Convert Date column to datetime
    all_star_df["Date"] = pd.to_datetime(all_star_df["Date"], errors="coerce")

    #Convert AL and NL scores to numeric
    all_star_df["AL"] = pd.to_numeric(all_star_df["AL"], errors="coerce")
    all_star_df["NL"] = pd.to_numeric(all_star_df["NL"], errors="coerce")

    #Remove rows with missing critical values
    all_star_df = all_star_df.dropna(subset=["Date", "AL", "NL"])

    #Create new column: Year (for analysis)
    all_star_df["Year"] = all_star_df["Date"].dt.year

    #Create new column: Total Runs 
    all_star_df["Total_Runs"] = all_star_df["AL"] + all_star_df["NL"]


    print("\nAfter Cleaning")
    print("Shape:", all_star_df.shape)
    print("\nMissing values:\n", all_star_df.isnull().sum())
    print("\nDuplicate rows:", all_star_df.duplicated().sum())
    print("\nSample Data:")
    print(all_star_df.head())

    return all_star_df

 # ===========================================================================================
 # PART 4: CLEANING - AWARDS
 # ===========================================================================================

def clean_awards(mvp_df, cy_young_df, rookie_df):
    """
    Clean award datasets (MVP, Cy Young, Rookie of the Year):
    - Remove duplicates 
    - Remove placeholder/header rows
    - Convert Year and numeric columns
    - Drop rows with missing critical values
    """
    print("\nBEFORE CLEANING - Awards")

    # Print basic info for each award
    for df, name in zip([mvp_df, cy_young_df, rookie_df], 
                    ["All-Star MVP Award", "CY Young Award", "Rookie of the Year Award"]):
        print(f"\n{name}:")
        print("Shape:", df.shape)
        print("Missing values:\n", df.isnull().sum())
        print("Duplicate rows:", df.duplicated().sum())
        print("Sample data:")
        print(df.head())

    # ---------------------Clean MVP Award--------------------------------------------------
    mvp_df = mvp_df.drop_duplicates()  #Remove duplicate rows
    # Remove placeholder rows in Name or Team
    mvp_df = mvp_df[~mvp_df["Name"].str.contains("Winner|All-Star MVP Award", na=False)]
    mvp_df = mvp_df[~mvp_df["Team"].str.contains("Team \\(Qty\\)", na=False)]
    # Convert Year column to numeric
    mvp_df["Year"] = pd.to_numeric(mvp_df["Year"], errors="coerce")
    mvp_df = mvp_df.dropna(subset=["Year", "Name", "Team", "Position"]) #Remove rows with missing critical values
    mvp_df["Year"] = mvp_df["Year"].astype(int)

    # --------------------Clean CY Young Award-------------------------------------------------
    cy_young_df = cy_young_df.drop_duplicates()  #Remove duplicate rows
    # Remove placeholder rows in Name or Team
    cy_young_df = cy_young_df[~cy_young_df["Name"].str.contains("Winner|CY Young Award", na=False)]
    cy_young_df = cy_young_df[~cy_young_df["Team"].str.contains("Team \\(Qty\\)", na=False)]
    # Convert Year column to numeric
    cy_young_df["Year"] = pd.to_numeric(cy_young_df["Year"], errors="coerce")
    # Convert numeric stats columns
    numeric_cols = ["TH", "W-L", "ERA", "IP", "SO", "SV"]
    for col in numeric_cols:
        if col in cy_young_df.columns:
            cy_young_df[col] = pd.to_numeric(cy_young_df[col], errors="coerce")
    cy_young_df = cy_young_df.dropna(subset=["Year", "Name", "Team"]) #Remove rows with missing critical values

    # -------------------Clean Rookie of the Year Award--------------------------------------------
    rookie_df = rookie_df.drop_duplicates()  #Remove duplicate rows
    # Remove placeholder rows in Name
    rookie_df = rookie_df[~rookie_df["Name"].str.contains("Winner|Rookie of the Year", na=False)]
    rookie_df = rookie_df[~rookie_df["Team"].str.contains("Team \\(Qty\\)", na=False)]
    # Convert Year column to numeric
    rookie_df["Year"] = pd.to_numeric(rookie_df["Year"], errors="coerce")
    rookie_df = rookie_df.dropna(subset=["Year", "Name", "Team", "Position"]) #Remove rows with missing critical values
    # ------------------------Summary after cleaning--------------------------------------------

    print("\nAFTER CLEANING - Awards")

    for df, name in zip([mvp_df, cy_young_df, rookie_df],
                    ["All-Star MVP Award", "CY Young Award", "Rookie of the Year Award"]):
        print(f"\n{name}:")
        print("Shape:", df.shape)
        print("Missing values:\n", df.isnull().sum())
        print("Duplicate rows:", df.duplicated().sum())
        print("Sample data:")
        print(df.head())

    print("\nAll Awards cleaned successfully")

    return mvp_df, cy_young_df, rookie_df

# ===========================================================================================
# PART 5: CLEANING - MANAGERS DATA
# ===========================================================================================

def clean_managers(managers_df):
    """
    Clean Managers dataset:
    - Remove duplicates
    - Split Year column into Start_Year and End_Year
    - Convert year columns to numeric
    - Remove rows with missing essential values
    """
    print("BEFORE CLEANING")
    print("Shape:", managers_df.shape)
    print("\n Missing values:\n",managers_df.isnull().sum())
    print("\nDuplicate rows:", managers_df.duplicated().sum())
    print("Sample data:")
    print(managers_df.head())

    #Remove duplicate rows
    managers_df = managers_df.drop_duplicates()

    # Split Years column into Start_Year and End_Year
    if "Years" in managers_df.columns:
        years_split = managers_df["Years"].str.split("-", expand=True)
        managers_df["Start_Year"] = pd.to_numeric(years_split[0], errors="coerce")
        managers_df["End_Year"] = pd.to_numeric(years_split[1], errors="coerce")
    #Remove rows with missing critical values
    managers_df = managers_df.dropna(subset=["Team", "Manager", "Start_Year", "End_Year"])
    
    managers_df["Start_Year"] = managers_df["Start_Year"].astype(int)
    managers_df["End_Year"] = managers_df["End_Year"].astype(int)

    print("\nAfter Cleaning")
    print("Shape:", managers_df.shape)
    print("\nMissing values:\n", managers_df.isnull().sum())
    print("\nDuplicate rows:", managers_df.duplicated().sum())
    print("\nSample Data:")
    print(managers_df.head())

    return managers_df


all_star_df = clean_all_star(all_star_df)
mvp_df, cy_young_df, rookie_df = clean_awards(mvp_df, cy_young_df, rookie_df)
managers_df = clean_managers(managers_df)

# =============================================================================================
# PART 6 - SAVE CLEANED DATA BACK TO DATABASE
# ==============================================================================================

with sqlite3.connect("mlb_history.db") as conn:
    all_star_df.to_sql("all_star_game", conn, if_exists="replace", index=False)
    mvp_df.to_sql("all_star_mvp_award", conn, if_exists="replace", index=False)
    cy_young_df.to_sql("cy_young_award", conn, if_exists="replace", index=False)
    rookie_df.to_sql("rookie_of_the_year_award", conn, if_exists="replace", index=False)
    managers_df.to_sql("managers", conn, if_exists="replace", index=False)

print("Cleaned data saved back to the database successfully")