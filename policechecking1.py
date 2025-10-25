

import streamlit as st
import pandas as pd
import pymysql
import plotly.express as plt


# Database connection
def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='deen1234',
            database='police_check_point',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Fetch data from database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    
# STREAMLIT UI
st.set_page_config(page_title="police_check_point DASHBOARD", layout="wide")

st.title("🚨police_check_point: Police Check Post Digital Ledger")
st.markdown("REAL_TIME MONITORING AND INSIGHT FOR LAW ENFOREMENT🚓")

#SHOW FULL TABLE


st.header("POLICE OVERVIEW")
query = "SELECT * FROM police_check_process1"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

# QUICK METRICS
st.header ("📊key matrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Number of police stop", total_stops)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest",case=False, na=False)].shape[0]
    st.metric("Number of Arrest", arrests)

with col3:
    warning =data[data['stop_outcome'].str.contains("warning",case=False, na=False)].shape[0]
    st.metric("Number of warning",warning)

with col4:
    drug_related =data[data['drugs_related_stop']== 1].shape[0]
    st.metric("drugs related stops",drug_related)


            
# ADVANCED QUERIES
st.header ("Advanced Insights")

selected_query = st.selectbox("Select a Query to Run", [
    "What are the top 10 vehicle_Number involved in drug-related stops",
    "Which vehicles were most frequently searched",
    "Which driver age group had the highest arrest rate",
    "What is the gender distribution of drivers stopped in each country",
    "Which race and gender combination has the highest search rate",
    "What time of day sees the most traffic stops",
    "What is the average stop duration for different violations",
    "Are stops during the night more likely to lead to arrests",
    "Which violations are most associated with searches or arrests",
    "Which violations are most common among younger drivers (<25)",
    "Is there a violation that rarely results in search or arrest",
    "Which countries report the highest rate of drug-related stops",
    "What is the arrest rate by country and violation",
    "Which country has the most stops with search conducted",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops, Number of Stops by Year,Month, Hour of the Day",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
])
query_map= {
    "What are the top 10 vehicle_Number involved in drug-related stops": "SELECT vehicle_number, COUNT(*) AS stop_count FROM police_check_process1 GROUP BY vehicle_number ORDER BY stop_count DESC LIMIT 10",

    "Which vehicles were most frequently searched":"SELECT vehicle_number, COUNT(*) AS search_count FROM police_check_process1 WHERE search_conducted = 1 GROUP BY vehicle_number ORDER BY search_count DESC",

    "Which driver age group had the highest arrest rate": """SELECT driver_age,COUNT(CASE WHEN stop_outcome = "Arrest" THEN 1 END) * 100.0 / COUNT(*) AS is_arrested FROM Police_check_process1 GROUP BY driver_age ORDER BY is_arrested DESC""",
   
    "What is the gender distribution of drivers stopped in each country": "SELECT country_name,driver_gender, COUNT(*) AS stop_count FROM police_check_process1 GROUP BY country_name, driver_gender ORDER BY country_name, stop_count DESC",

    "Which race and gender combination has the highest search rate": """SELECT driver_race, driver_gender,COUNT(CASE WHEN search_conducted = 1 THEN 1 END) * 100.0 / COUNT(*) AS search_rate FROM police_check_process1
        GROUP BY driver_race, driver_gender ORDER BY search_rate DESC""",

    "What time of day sees the most traffic stops": " SELECT DATE_FORMAT(stop_time, '%H') AS hour, COUNT(*) AS stop_count FROM police_check_process1 GROUP BY hour ORDER BY stop_count DESC",
    
    "What is the average stop duration for different violations": """ SELECT violation_raw, AVG(CASE stop_duration 
    WHEN '0-15 Min' THEN 7.5 
    WHEN '15-30 Min' THEN 22.5 WHEN '30-45 Min' THEN 37.5
    WHEN '45-60 Min' THEN 52.5 WHEN '60+ Min' THEN 65  ELSE NULL  END  ) AS average_stop_duration_minutes FROM Police_check_process1 GROUP BY violation_raw ORDER BY  average_stop_duration_minutes DESC """,

    "Are stops during the night more likely to lead to arrests": """SELECT CASE 
    WHEN HOUR(stop_time) BETWEEN 20 AND 23 THEN 'Night'
    WHEN HOUR(stop_time) BETWEEN 0 AND 5 THEN 'Night'
    ELSE 'Day'END AS time_of_day,COUNT(CASE WHEN stop_outcome = 'Arrest' THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate FROM police_check_process1  GROUP BY time_of_day""",

    "Which violations are most associated with searches or arrests": """SELECT violation,COUNT(CASE WHEN search_conducted = 1 THEN 1 END) AS search_count,COUNT(CASE WHEN is_arrested = 1 THEN 1 END) AS arrest_count
        FROM police_check_process1 GROUP BY violation ORDER BY (search_count + arrest_count) DESC  """,

    "Which violations are most common among younger drivers (<25)": " SELECT violation, COUNT(*) AS stop_count FROM police_check_process1 WHERE driver_age < 25 GROUP BY violation ORDER BY stop_count DESC",

    "Is there a violation that rarely results in search or arrest": """SELECT violation,COUNT(*) AS total_stops,AVG(CASE WHEN search_conducted = 1 OR is_arrested = 1 THEN 1.0 ELSE 0 END) AS action_rate
        FROM police_check_process1 GROUP BY violation ORDER BY total_stops DESC""",

    "Which countries report the highest rate of drug-related stops": """SELECT country_name, COUNT(*) AS total_stops, COUNT(CASE WHEN LOWER(violation) LIKE '%drug%' THEN 1 END) AS drug_stops
        FROM police_check_process1 GROUP BY country_name ORDER BY drug_stops DESC""",

    "What is the arrest rate by country and violation": """SELECT country_name, violation_raw, COUNT(CASE WHEN is_arrested = 1 THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
        FROM police_check_process1 GROUP BY country_name, violation_raw ORDER BY arrest_rate DESC """,

    "Which country has the most stops with search conducted": "SELECT country_name, COUNT(*) AS search_count FROM police_check_process1 WHERE search_conducted = 1 GROUP BY country_name ORDER BY search_count DESC",
    

    "Yearly Breakdown of Stops and Arrests by Country": """SELECT country_name, YEAR(stop_time) AS year,COUNT(*) AS total_stops,COUNT(CASE WHEN is_arrested = 1 THEN 1 END) AS arrests
        FROM police_check_process1 GROUP BY country_name, year ORDER BY country_name, year""",

    "Driver Violation Trends Based on Age and Race": "SELECT driver_age, driver_race, violation, COUNT(*) AS stop_count FROM police_check_process1 GROUP BY driver_age, driver_race, violation ORDER BY stop_count DESC",

    "Time Period Analysis of Stops, Number of Stops by Year,Month, Hour of the Day": """ SELECT YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS year,MONTH(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS month,
    CAST(SUBSTRING_INDEX(stop_time, ':', 1) AS UNSIGNED) AS hour,COUNT(*) AS stop_count FROM police_check_process1 WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL GROUP BY year, month, hour ORDER BY year, month, hour""",

    "Violations with High Search and Arrest Rates": """SELECT violation,COUNT(CASE WHEN search_conducted = 1 THEN 1 END) * 100.0 / COUNT(*) AS search_rate,
       COUNT(CASE WHEN is_arrested = 'TRUE' THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate FROM police_check_process1 GROUP BY violation ORDER BY (search_rate + arrest_rate) DESC """,

    "Driver Demographics by Country (Age, Gender, and Race)": """SELECT country_name, driver_age, driver_gender, driver_race, COUNT(*) AS stop_count FROM police_check_process1
     GROUP BY country_name, driver_age, driver_gender, driver_race ORDER BY country_name, stop_count DESC""",
    
    "Top 5 Violations with Highest Arrest Rates": """SELECT violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS arrests,SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS arrest_rate
FROM police_check_process1 GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5"""

}


# Run selected query
if st.button("Run Query"):
    result  = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results")

st.markdown("---")
st.markdown("LAW ENFORCEMENT BY POLICE CHECK")
st.header("custom filter")

st.markdown ("FILL IN THE BELOW DETAILS")


st.header("Add new police logg & predict outcome and violation")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("country name")
    driver_gender = st.selectbox(" Driver Gender",{"male","female"})
    driver_age = st.number_input("Driver Age",min_value=16,max_value=100, value=27)
    search_conducted =st.selectbox("was search conducted?",["0","1"])
    search_type = st.text_input("search type")
    drugs_related_stop = st.selectbox(" it drug related?",["0","1"])
    stop_duration = st.selectbox("stop duration",data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("vehicle number")
    timestamp = pd.Timestamp.now()


    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    if submitted:

        # Filter data for prediction
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # Predict stop_outcome
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning"  # Default fallback
            predicted_violation = "speeding"  # Default fallback

        # Natural language summary
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

        st.markdown(f"""
        🚔 **Prediction Summary**

        - **Predicted Violation:** {predicted_violation}
        - **Predicted Stop Outcome:** {predicted_outcome}

        🗒️ A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.  
        {search_text}, and the stop {drug_text}.  
        Stop duration: **{stop_duration}**.
        Vehicle Number: **{vehicle_number}**.
        """)