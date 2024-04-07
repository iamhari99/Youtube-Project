# YouTube Data Harvesting and Warehousing using SQL and Streamlit

## Inroduction
This project collects data from YouTube channels using the YouTube Data API, stores it in a MySQL database, and provides functionalities to analyze the collected data through Streamlit.

## Technology Stack Used
1. Python
2. Streamlit
3. google-api-python-client
4. SQLAlchemy
5. MySQL

You can install these dependencies using pip:
pip install streamlit google-api-python-client SQLAlchemy mysql-connector-python


## Setup

1. Obtain YouTube Data API Key: Obtain an API key from the Google Cloud Console for the YouTube Data API v3.
2. MySQL Database Setup: Make sure you have a MySQL database set up where you want to store the collected data. Update the database connection details (host, username, password, database name) in the code accordingly.
3. Run the Application: Run the main Python script (main.py). It will launch a Streamlit web application in your browser.

## Approach

- Retrieve data from the YouTube API, including channel information, playlists, videos, and comments.
- Store the retrieved data temporarily as Pandas Dataframe.
- Migrate the data to a SQL data warehouse.
- Analyze and visualize data using Streamlit.
- Perform queries on the SQL data warehouse using mysql connector.
- Gain insights into channel performance, video metrics, and more.

## Contact

📧 Email: hariharandvanitha@gmail.com

🌐 LinkedIn: www.linkedin.com/in/hariharan-d

