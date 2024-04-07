import streamlit as st
from googleapiclient.discovery import build
from sqlalchemy import create_engine, VARCHAR, TEXT, DATETIME, INTEGER
from urllib.parse import quote_plus
import pandas as pd
import mysql.connector

# Function to initialize YouTube API client
def initialize_youtube_api():
    api_key= 'AIzaSyAUDYwSYK9ZiTRPWkAzkVbnfwiDQmRITQ0'
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)
    return youtube

# Function to get channel information
def get_channel_info(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet, contentDetails, statistics, status",
        id=channel_id
    )
    response = request.execute()
    for item in response['items']:
        data = {
            'Channel_Name': item["snippet"]["title"],
            'Channel_Id': item["id"], 
            'Channel_Views': item["statistics"]["viewCount"],
            'Channel_Description': item["snippet"]["description"],
            'Channel_Type': item["status"]["privacyStatus"]
        }
    return data

# Function to get video IDs
def get_video_ids(youtube, channel_id):
    video_ids = []
    response = youtube.channels().list(
        id=channel_id,
        part='contentDetails'
    ).execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token = None

    while True:
        playlist_items_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        
        for item in playlist_items_response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
        next_page_token = playlist_items_response.get('nextPageToken')
                                      
        if next_page_token is None:
            break

    return video_ids

# Function to get video information
def get_video_info(youtube, video_ids):
    video_data = []

    for video_id in video_ids:
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        ).execute()

        for item in response["items"]:
            data = {
                'Channel_Id': item['snippet']['channelId'],
                'Video_Id': item['id'],
                'Video_Name': item['snippet']['title'],
                'Playlist_Id': item['snippet'].get('playlistId'),
                'Thumbnail': item['snippet']['thumbnails']['default']['url'],
                'Video_Description': item['snippet'].get('description'),
                'Published_Date': item['snippet']['publishedAt'],
                'Duration': item['contentDetails']['duration'],
                'Views': item['statistics'].get('viewCount'),
                'Like_count' : item['statistics'].get('likeCount'),
                'Dislike_count' : item['statistics'].get('dislikeCount'),
                'Comment_Count': item['statistics'].get('commentCount'),
                'Favorite_Count': item['statistics']['favoriteCount'],
                'Caption_Status': item['contentDetails']['caption']
            }
            video_data.append(data)
    return video_data

# Function to get comment information
def get_comment_info(youtube, video_ids):
    comment_data = []

    for video_id in video_ids:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100
            ).execute()

            for cmt in response['items']:
                data = {
                    'Comment_id': cmt['id'],
                    'Video_id': cmt['snippet']['videoId'],
                    'Comment_text': cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                    'Comment_author': cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'Comment_published_date': cmt['snippet']['topLevelComment']['snippet']['publishedAt']
                }
                comment_data.append(data)
        except:
            pass

    return comment_data

# Function to get playlist information
def get_playlist_details(youtube, channel_id):
    next_page_token = None
    playlist_data = []
    
    while True:
        response = youtube.playlists().list(
            part='snippet,contentDetails', 
            channelId=channel_id, 
            maxResults=50, 
            pageToken=next_page_token
        ).execute()
        
        for item in response['items']:
            data = {
                'Playlist_Id': item['id'],
                'Playlist_Name': item['snippet']['title'],
                'Channel_Id': item['snippet']['channelId'],
            }
            playlist_data.append(data)
            
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            break

    return playlist_data

# Function to execute MySQL queries
def execute_query(query):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Shyam1234@",
        database="youtube"
    )
    cursor = connection.cursor()

    # Execute query
    cursor.execute(query)
    result = cursor.fetchall()

    # Close connection
    cursor.close()
    connection.close()

    return result

# Display list of 10 questions in the sidebar
def display_questions_and_execute_queries():
    questions = st.selectbox("Select your questions",["1. What are the names of all the videos and their corresponding channels?",
                                                      "2. Which channels have the most number of videos, and how many videos do they have?",
                                                      "3. What are the top 10 most viewed videos and their respective channels?",
                                                      "4. How many comments were made on each video, and what are their corresponding video names?",
                                                      "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                                                      "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                                                      "7. What is the total number of views for each channel, and what are their corresponding channel names?",
                                                      "8. What are the names of all the channels that have published videos in the year 2022?",
                                                      "9. Which videos have the highest number of comments, and what are their corresponding channel names?",
                                                      "10. What is the average duration of all videos in each channel, and what are their corresponding channel names?"])

    # Execute MySQL queries to answer the questions
    if questions == "1. What are the names of all the videos and their corresponding channels?":
        query1 = '''SELECT Video_Name, Channel_Name 
                    FROM videos 
                    INNER JOIN channels ON videos.Channel_Id = channels.Channel_Id'''
        result = execute_query(query1)
        df = pd.DataFrame(result, columns=['Video Title', 'Channel Name'])
        st.write(df)
    
    elif questions == "2. Which channels have the most number of videos, and how many videos do they have?":
        query2 = '''SELECT Channel_Name, COUNT(*) AS Video_Count
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    GROUP BY channels.Channel_Name
                    ORDER BY Video_Count DESC'''
        result = execute_query(query2)
        df = pd.DataFrame(result, columns=['Channel Name', 'Video Count'])
        st.write(df)

    elif questions == "3. What are the top 10 most viewed videos and their respective channels?":
        query3 = '''SELECT Video_Name, Channel_Name, Views
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    ORDER BY Views DESC
                    LIMIT 10'''
        result = execute_query(query3)
        df = pd.DataFrame(result, columns=['Video Title', 'Channel Name', 'Views'])
        st.write(df)

    elif questions == "4. How many comments were made on each video, and what are their corresponding video names?":
        query4 = '''SELECT videos.Video_Name, COUNT(*) AS Comment_Count
                    FROM youtube.videos 
                    INNER JOIN youtube.comments ON videos.Video_Id = comments.Video_id
                    GROUP BY videos.Video_Id, videos.Video_Name'''
        result = execute_query(query4)
        df = pd.DataFrame(result, columns=['Video Title', 'Comment Count'])
        st.write(df)

    elif questions == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
        query5 = '''SELECT Video_Name, Channel_Name, Like_count
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    ORDER BY Like_count DESC
                    LIMIT 10'''
        result = execute_query(query5)
        df = pd.DataFrame(result, columns=['Video Title', 'Channel Name', 'Like Count'])
        st.write(df)

    elif questions == "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        query6 = '''SELECT Video_Name, SUM(Like_count) AS Total_Likes, SUM(Dislike_count) AS Total_Dislikes
                    FROM youtube.videos
                    GROUP BY Video_Name'''
        result = execute_query(query6)
        df = pd.DataFrame(result, columns=['Video Title', 'Total Likes', 'Total Dislikes'])
        st.write(df)

    elif questions == "7. What is the total number of views for each channel, and what are their corresponding channel names?":
        query7 = '''SELECT Channel_Name, SUM(Views) AS Total_Views
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    GROUP BY Channel_Name'''
        result = execute_query(query7)
        df = pd.DataFrame(result, columns=['Channel Name', 'Total Views'])
        st.write(df)

    elif questions == "8. What are the names of all the channels that have published videos in the year 2022?":
        query8 = '''SELECT DISTINCT Channel_Name as Published_Year
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    WHERE YEAR(Published_Date) = 2022
                    group by Channel_Name'''
        result = execute_query(query8)
        df = pd.DataFrame(result, columns=['Channel Name'])
        st.write(df)

    elif questions == "9. Which videos have the highest number of comments, and what are their corresponding channel names?":
        query9 = '''SELECT v.Video_Name, ch.Channel_Name, COUNT(*) AS Comment_Count
                    FROM youtube.videos AS v
                    INNER JOIN youtube.comments AS c ON v.Video_Id = c.Video_id
                    INNER JOIN youtube.channels AS ch ON v.Channel_Id = ch.Channel_Id
                    GROUP BY v.Video_Name, ch.Channel_Name
                    ORDER BY Comment_Count DESC
                    LIMIT 10;'''
        result = execute_query(query9)
        df = pd.DataFrame(result, columns=['Video Title', 'Channel Name', 'Comment Count'])
        st.write(df)

    elif questions == "10. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        query10 = '''SELECT Channel_Name, AVG(Duration) AS Average_Duration
                    FROM youtube.videos 
                    INNER JOIN youtube.channels ON videos.Channel_Id = channels.Channel_Id
                    GROUP BY Channel_Name'''
        result = execute_query(query10)
        df = pd.DataFrame(result, columns=['Channel Name', 'Average Duration'])
        st.write(df)



# Main function
def main():
    st.title(':blue[YouTube Data Harvesting and Warehousing]')

    # Get user input for channel ID
    channel_id = st.text_input('Enter YouTube Channel ID:')
    button_clicked = st.button('Collect and Transfer Data to SQL')

    # Initialize YouTube API and get data if button is clicked
    if button_clicked:
        youtube = initialize_youtube_api()
        channel_info = get_channel_info(youtube, channel_id)
        video_ids = get_video_ids(youtube, channel_id)
        video_info = get_video_info(youtube, video_ids)
        comment_info = get_comment_info(youtube, video_ids)
        playlist_info = get_playlist_details(youtube, channel_id)

        # Convert data to DataFrames
        channel_df = pd.DataFrame([channel_info])
        video_df = pd.DataFrame(video_info)
        comment_df = pd.DataFrame(comment_info)
        playlist_df = pd.DataFrame(playlist_info)

        # Display a success message
        st.success('Data collected successfully!')

        # Display the collected data
        st.subheader('Channel Information')
        st.dataframe(channel_df)

        st.subheader('Video Information')
        st.dataframe(video_df)

        st.subheader('Comment Information')
        st.dataframe(comment_df)

        st.subheader('Playlist Information')
        st.dataframe(playlist_df)

        # Transfer data to SQL database
        transfer_to_sql(channel_df, video_df, comment_df, playlist_df)

    # Display questions and execute MySQL queries
    display_questions_and_execute_queries()
    

# Function to transfer data to SQL database       
def transfer_to_sql(channel_df, video_df, comment_df, playlist_df):
    # Define MySQL connection string
    mysql_password = 'Shyam1234@'
    encoded_password = quote_plus(mysql_password)
    mysql_connection_string = f'mysql+pymysql://root:{encoded_password}@localhost:3306/youtube'

    # Create SQLAlchemy engine
    engine = create_engine(mysql_connection_string)

    # Convert columns into datetime objects
    video_df['Published_Date'] = pd.to_datetime(video_df['Published_Date'])
    comment_df['Comment_published_date'] = pd.to_datetime(comment_df['Comment_published_date'])

    # Define data types for each column
    channel_dtypes = {'Channel_Name': VARCHAR(255), 'Channel_Id': VARCHAR(255), 'Channel_Views': INTEGER, 'Channel_Description': TEXT, 'Channel_Type': TEXT}
    video_dtypes = {'Channel_Id': VARCHAR(255), 'Video_Id': VARCHAR(255), 'Video_Name': TEXT, 'Playlist_Id': VARCHAR(255), 'Thumbnail': VARCHAR(255), 'Video_Description': TEXT, 'Published_Date': DATETIME, 'Duration': VARCHAR(255), 'Views': INTEGER,'Like_count': INTEGER, 'Dislike_count' : INTEGER, 'Comment_Count': INTEGER, 'Favorite_Count': INTEGER, 'Caption_Status': VARCHAR(255)}
    comment_dtypes = {'Comment_id': VARCHAR(255), 'Video_id': VARCHAR(255), 'Comment_text': TEXT, 'Comment_author': VARCHAR(255), 'Comment_published_date': DATETIME}
    playlist_dtypes = {'Playlist_Id': VARCHAR(255), 'Playlist_Name': TEXT, 'Channel_Id': VARCHAR(255)}

    # Append data to existing tables with specified data types
    channel_df.to_sql('channels', con=engine, if_exists='append', index=False, dtype=channel_dtypes)
    video_df.to_sql('videos', con=engine, if_exists='append', index=False, dtype=video_dtypes)
    comment_df.to_sql('comments', con=engine, if_exists='append', index=False, dtype=comment_dtypes)
    playlist_df.to_sql('playlists', con=engine, if_exists='append', index=False, dtype=playlist_dtypes)

    # Dispose the engine after use
    engine.dispose()

if __name__ == "__main__":
    main()