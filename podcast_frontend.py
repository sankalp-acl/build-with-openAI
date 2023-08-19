import streamlit as st
import modal
import json
import os
import altair as alt
import pandas as pd

# add a custom css file
st.markdown(
    f"<style>{open('custom.css').read()}</style>",
    unsafe_allow_html=True,
)

# add a custom favicon
st.markdown(
    """<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">""",
    unsafe_allow_html=True,
)

# Initialize session state
if 'selected_podcast' not in st.session_state:
    st.session_state.selected_podcast = None

def main():
    # Add a background image
    st.image('img/podcast_gif.gif', use_column_width=True)

    # st.title("Podcast Dashboard")
    st.markdown(f"<h1 style='color: white;'>Podcast Dashboard</h1>", unsafe_allow_html=True)

    available_podcast_info = create_dict_from_json_files('.')
    
    # Sidebar search feature
    st.sidebar.header("Search Podcasts")    
    search_query = st.sidebar.text_input("Suggestions: XAI, Biden, Pizza, etc.", placeholder="Type keyword and press enter to search...")

    if search_query:
        matching_podcasts = find_matching_podcasts(search_query, available_podcast_info)
        if matching_podcasts:
            st.sidebar.subheader("Matching Podcasts")
            for podcast_name in matching_podcasts:
                # Make the podcast name clickable
                if st.sidebar.button(podcast_name, key=podcast_name):
                    # Set the selected podcast in the session state
                    st.session_state.selected_podcast = podcast_name
                    #display_podcast_details(podcast_name, available_podcast_info)

    # add horizontal line
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    
    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox("Select Podcast", options=available_podcast_info.keys(),
                                            index=get_selected_podcast_index(st.session_state.selected_podcast, available_podcast_info))

    if selected_podcast:

        podcast_info = available_podcast_info[selected_podcast]

        # Right section - Newsletter content
        # st.header("Newsletter Content")
        st.markdown(f"<h2 style='color: #999afd;'>Podcast Content</h2>", unsafe_allow_html=True)
        

        # Display the podcast title
        # st.subheader("Episode Title")
        st.markdown(f"<h3 style='color: #f582ff;'>Episode Title</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin-bottom: 5px; color: #FFDB58;'>{podcast_info['podcast_details']['episode_title']}</p>", unsafe_allow_html=True)

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            # st.subheader("Podcast Episode Summary")
            st.markdown(f"<h3 style='color: #f582ff;'>Podcast Episode Summary</h3>", unsafe_allow_html=True)
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            # st.subheader("Podcast Guest")
            st.markdown(f"<h3 style='color: #f582ff;'>Podcast Guest</h3>", unsafe_allow_html=True)
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            # st.subheader("Podcast Guest Details")
            st.markdown(f"<h3 style='color: #f582ff;'>Podcast Guest Details</h3>", unsafe_allow_html=True)
            st.write(podcast_info["podcast_guest"]['summary'])
            
        # add a horizontal line
        st.markdown("<hr>", unsafe_allow_html=True)

        # Display the five key moments
        # st.subheader("Key Moments")
        st.markdown(f"<h3 style='color: #f582ff;'>Key Moments</h3>", unsafe_allow_html=True)
        key_moments = podcast_info['podcast_highlights']
        key_highlights = podcast_info['podcast_highlights'].split('\n')
        
        st.markdown(f"<p style='margin-bottom: 15px; color: #FFDB58;'><i>Key highlights from the podcast transcription are:</i></p>", unsafe_allow_html=True)
        for moment in key_highlights:
            if 'key highlights' in moment.lower() or moment == '':
                pass
            else:
                moment = moment.strip('-')
                st.markdown(
                    f"<div style='margin-bottom: 5px; display: flex; align-items: top;'><i class='fa fa-star' style='color: rgb(51 198 142); margin-top: 5px;'></i><span style='margin-left: 12px;'>{moment}</span></div>",
                    unsafe_allow_html=True
                )
                 
        # add a horizontal line
        st.markdown("<hr>", unsafe_allow_html=True)
                
        # add horizontal line
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
           
        # Display the key moments timeline chart
        # st.subheader("Key Moments Timeline")
        st.markdown(f"<h3 style='color: #f582ff;'>Key Moments Timeline</h3>", unsafe_allow_html=True)
        
        # add a subheader, small in font-size and in italics
        st.markdown(
            f"<p style='font-size: small; margin-bottom: 20px; color: #FFDB58;font-style: italic;'>Coming soon! The chart below shows the time distribution of key moments in the podcast episode.</p>", unsafe_allow_html=True)
        timeline_data = pd.DataFrame({'Moment': key_highlights, 'Time': range(1, len(key_highlights) + 1)})
        chart = alt.Chart(timeline_data).mark_bar().encode(
            x='Time:O',
            y='count():Q',
            color=alt.Color('Time:O', scale=alt.Scale(scheme='viridis'))
        ).properties(
            width=600,
            height=150
        )
        st.altair_chart(chart)

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed", placeholder="Enter the RSS Feed URL here...")

    process_button = st.sidebar.button("Process Podcast Feed")
    st.sidebar.markdown(f"<p style='color: #f369ff;'><i><strong>Note:</strong> Podcast processing can take upto 5 mins, please be patient.</i></p>", unsafe_allow_html=True)

    if process_button:

        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast_info(url)

        # Right section - Newsletter content
        st.header("Newsletter Content")

        # Display the podcast title
        st.subheader("Episode Title")
        st.markdown(f"<p style='margin-bottom: 5px; color: #FFDB58;'>{podcast_info['podcast_details']['episode_title']}</p>", unsafe_allow_html=True)

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
            
    # Created by section
    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='font-size: small; font-style: italic; margin-top: auto;'>Created by: <a href='https://sankalp-prabhakar.github.io/' target='_blank' style='color: pink;'>Sankalp Prabhakar</a></p>", unsafe_allow_html=True)

def find_matching_podcasts(query, podcast_info_dict):
    matching_podcasts = []
    for podcast_name, podcast_info in podcast_info_dict.items():
        if query.lower() in podcast_name.lower() or query.lower() in podcast_info['podcast_summary'].lower():
            matching_podcasts.append(podcast_name)
    return matching_podcasts

def display_podcast_details(podcast_name, podcast_info_dict):
    podcast_info = podcast_info_dict.get(podcast_name)
    if podcast_info:
        st.header(f"Details for {podcast_name}")
        # Display the podcast details here
        st.write("Podcast Summary:", podcast_info['podcast_summary'])
        # ... (add more podcast details as needed)
        
def get_selected_podcast_index(selected_podcast, available_podcast_info):
    if selected_podcast in available_podcast_info:
        return list(available_podcast_info.keys()).index(selected_podcast)
    return 0

def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/content/podcast/')
    return output

if __name__ == '__main__':
    main()
