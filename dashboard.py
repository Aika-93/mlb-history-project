""""
MLB Dashboard

Interactive dashboard to visualize MLB historical data:
 - Total Runs per Year 
 - Top Teams by Awards
 - Top MVPs by AL Runs
 Built with Dash and Plotly Express

"""

import pandas as pd
import sqlite3
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

#SQLite database file
DATABASE = "mlb_history.db"

# =========================
# Load Data from Database
# =========================

with sqlite3.connect(DATABASE) as conn:
    all_star_df = pd.read_sql("SELECT * FROM all_star_game", conn)
    mvp_df = pd.read_sql("SELECT * FROM all_star_mvp_award", conn)
    cy_young_df = pd.read_sql("SELECT * FROM cy_young_award", conn)
    rookie_df = pd.read_sql("SELECT * FROM rookie_of_the_year_award", conn)

# ====================
# Data Transformation 
# ====================

#Combine all awards into one DataFrame
awards_df = pd.concat([mvp_df, cy_young_df, rookie_df], ignore_index=True)

#Clean team names
awards_df["Team_Clean"] = awards_df["Team"].str.replace(r'\s*\(.*\)', '', regex=True)

#Ensure Year columns are integer
awards_df["Year"] = awards_df["Year"].astype(int)
all_star_df["Year"] = all_star_df["Year"].astype(int)

#Calculate total runs per year
runs_per_year = all_star_df.groupby("Year")[["AL", "NL", "Total_Runs"]].sum().reset_index()

#Calculate total awards per team
awards_per_team = awards_df.groupby("Team_Clean").size().reset_index(name="Num_Awards")
awards_per_team = awards_per_team.sort_values("Num_Awards", ascending=False)

#Merge MVPs with all_star runs for top MVP chart
mvp_with_runs = pd.merge(mvp_df, all_star_df, on="Year", how="left")
mvp_runs = mvp_with_runs.groupby("Name")["AL"].sum().reset_index().sort_values("AL", ascending=False)

# =====================
# Initialize Dash App
# =====================

app = Dash(__name__)

# ====================
# App Layout
# ====================

app.layout = html.Div([
    html.H1("MLB Dashboard", style={'text-align': 'center'}),
    
    #Total Runs per Year chart with year slider 
    html.H2("Al vs NL Total Runs per Year"),
    dcc.RangeSlider(
        id='year-slider',
        min=runs_per_year["Year"].min(),
        max=runs_per_year["Year"].max(),
        value=[runs_per_year["Year"].min(), runs_per_year["Year"].max()],
        marks={y: str(y) for y in range(runs_per_year["Year"].min(), runs_per_year["Year"].max()+1, 5)},
        step=1
    ),
    dcc.Graph(id='runs-chart'),

    #Top Teams by Awards treemap with dropdown highlight
    html.H2("Top Teams by Total Awards"),
    dcc.Dropdown(
        id='team-dropdown',
        options=[{'label': t, 'value': t} for t in awards_per_team["Team_Clean"]],
        placeholder="Select team to highlight"
    ),
    dcc.Graph(id='awards-chart'),

    #Top MVPs by AL runs chart
    html.H2("Top MVPs by Total AL Runs"),
    dcc.Graph(
        id='mvp-chart',
        figure=px.bar(mvp_runs.head(10), x="Name", y="AL", text="AL",
                      title="Top 10 MVPs by AL Runs in Games They Played",
                      color_discrete_sequence=["royalblue"])
    )
])

# ============================
# Callbacks for interactivity
# ============================

@app.callback(
    Output('runs-chart', 'figure'),
    Input('year-slider', 'value')
)
def update_runs_chart(year_range):
    filtered = runs_per_year[(runs_per_year["Year"] >= year_range[0]) & (runs_per_year["Year"] <= year_range[1])]
    fig = px.line(filtered, x="Year", y=["AL", "NL", "Total_Runs"], markers=True,
                  title="AL vs NL and Total Runs per Year")
    return fig
    
@app.callback(
    Output('awards-chart', 'figure'),
    Input('team-dropdown', 'value')
)
def update_awards_chat(selected_team):
    df = awards_per_team.copy()

    fig = px.treemap(
        df,
        path=["Team_Clean"],
        values="Num_Awards",
        color="Num_Awards",
        color_continuous_scale="Greens",
        color_discrete_map="identity",
        title="Top 10 Teams by Total Awards"
    )
    fig.update_traces(marker=dict(line=dict(width=1, color="white")))
    if selected_team:
        #Highlight selected team in treemap
        fig.data[0].marker.line.width = [
            4 if label == selected_team else 1
            for label in fig.data[0].labels
        ]
        fig.data[0].marker.line.color = [
            "black" if label == selected_team else "white"
            for label in fig.data[0].labels
        ]

    return fig

# =========================
# Run App
# =========================
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)