import streamlit as st 
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account

import pandas as pd
import base64
import json

# region --------------------  config  ------------------------------

st.set_page_config(layout='wide', page_title='Cinema Ranking', initial_sidebar_state='expanded')

st.markdown("""

<style>

    section[data-testid="stSidebar"] {
        width: 420px !important;
    }
    .css-1nm2qww {
        display: none;
    }
    .css-vk3wp9 {
        min-width: 419px;
        max-width: 420px;
    }
    button[title="View fullscreen"] {
        visibility: hidden;
    }
    section.main > div:has(~ footer ) {
        padding-bottom: 5px;
    }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 24px;
    }
    .block-container {
        padding-top: 5px;
    }
    img {
        border-radius: 5%;
    }
    p {
        line-height: 1em;
    }
    #tabs-bui715-tabpanel-0 > div:nth-child(1) > div > div:nth-child(2) > div > div > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(1) > div > div.css-ocqkz7.e1f1d6gn3 > div.css-17zpgat.e1f1d6gn1 {
        display: flex;
        justify-content: center;
        align-items: center;
    }

</style>

""", unsafe_allow_html=True)


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64); tutukito/koolkidsteel8@gmail.com', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOTJiYmNiY2IxNWM4ZWM2MDQxZTE3NmE3ZGJkY2NhYSIsInN1YiI6IjY0ZDg0NDg5ZDEwMGI2MDBhZGExOTE0YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.KDRfub8-zkbIjM0AcIcf82PnvilKNhwzjMDbBi4A9Wo'}

if 'page_num' not in st.session_state.keys():
    st.session_state.page_num = 1
if 'search_results' not in st.session_state.keys():
    st.session_state.search_results = []
if 'movie_details' not in st.session_state.keys():
    st.session_state.movie_details = {}
    
if 'added_movies_s' not in st.session_state.keys():
    st.session_state.added_movies_s = pd.DataFrame(columns=['id', 'title', 'director', 'lead', 'date_added']) 
if 'added_movies_a' not in st.session_state.keys():
    st.session_state.added_movies_a = pd.DataFrame(columns=['id', 'title', 'director', 'lead', 'date_added']) 
if 'added_movies_b' not in st.session_state.keys():
    st.session_state.added_movies_b = pd.DataFrame(columns=['id', 'title', 'director', 'lead', 'date_added']) 
if 'added_movies_c' not in st.session_state.keys():
    st.session_state.added_movies_c = pd.DataFrame(columns=['id', 'title', 'director', 'lead', 'date_added']) 
if 'added_movies_user' not in st.session_state.keys():
    st.session_state.added_movies_user = None
    
if 'logged_in' not in st.session_state.keys():
    st.session_state.logged_in = False
if 'user' not in st.session_state.keys():
    st.session_state.user = None

if 'db' not in st.session_state.keys():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    st.session_state.db = firestore.Client(credentials=creds, project="my-movie-ranking")

# endregion -------------------- ------ ------------------------------
    
# region --------------------  functions  ------------------------------

def sign_up():
    if st.session_state.s_user_input and st.session_state.s_pass_input and st.session_state.email_input:
        user_ref = st.session_state.db.collection('users')
        query_ref = user_ref.where(filter=FieldFilter("email", "==", st.session_state.email_input))
        if len(query_ref.get()) > 0:
            st.sidebar.warning('email already in use')
            return
        doc = user_ref.document(st.session_state.s_user_input).get()
        if doc.exists:
            st.sidebar.warning('this username is already taken')
            return
        else:
            data = {'addedMoviesS': [], 'addedMoviesA': [], 'addedMoviesB': [], 'addedMoviesC': [], 'email': st.session_state.email_input, 'pass': st.session_state.s_pass_input}
            st.session_state.db.collection("users").document(st.session_state.s_user_input).set(data)     
            st.session_state.user = st.session_state.s_user_input
            st.session_state.logged_in = True
            st.session_state.s_user_input = None
            st.session_state.s_pass_input = None
            st.session_state.email_input = None
    else:
        st.sidebar.warning('please enter a valid value for each field')
        return
   
def authenticate():
    if st.session_state.user_input and st.session_state.pass_input:
        user_ref = st.session_state.db.collection('users').document(st.session_state.user_input)
        doc = user_ref.get()
        if doc.exists:
            user_info = doc.to_dict()
            if st.session_state.pass_input == user_info['pass']:
                st.session_state.user = st.session_state.user_input
                st.session_state.added_movies_user = st.session_state.user_input
                st.session_state.logged_in = True
                st.session_state.user_input = None
                st.session_state.pass_input = None
                added_movies_s = user_info['addedMoviesS']
                added_movies_a = user_info['addedMoviesA']
                added_movies_b = user_info['addedMoviesB']
                added_movies_c = user_info['addedMoviesC']
                if len(added_movies_s) > 0:
                    st.session_state.added_movies_s = pd.DataFrame(added_movies_s)
                if len(added_movies_a) > 0:
                    st.session_state.added_movies_a = pd.DataFrame(added_movies_a)
                if len(added_movies_b) > 0:
                    st.session_state.added_movies_b = pd.DataFrame(added_movies_b)
                if len(added_movies_c) > 0:
                    st.session_state.added_movies_c = pd.DataFrame(added_movies_c)
                
            else:
                st.sidebar.warning('incorrect username or password')
                return
        else:
            st.sidebar.warning('incorrect username or password')
            return
    else:
        st.sidebar.warning('please enter a valid username and password')
        return
        
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    
    
def remove_movie(id, tier):
    user_ref = st.session_state.db.collection('users').document(st.session_state.user)
    ## remove movie in state belonging to ^ tier
    if tier == 's':
        movies = st.session_state.added_movies_s
        movies.drop(movies[movies['id'] == id].index, inplace = True)
        st.session_state.added_movies_s = movies
        user_ref.set({'addedMoviesS': st.session_state.added_movies_s.to_dict('records')}, merge=True)
    elif tier == 'a':
        movies = st.session_state.added_movies_a
        movies.drop(movies[movies['id'] == id].index, inplace = True)
        st.session_state.added_movies_a = movies
        user_ref.set({'addedMoviesA': st.session_state.added_movies_a.to_dict('records')}, merge=True)
    elif tier == 'b':
        movies = st.session_state.added_movies_b
        movies.drop(movies[movies['id'] == id].index, inplace = True)
        st.session_state.added_movies_b = movies
        user_ref.set({'addedMoviesB': st.session_state.added_movies_b.to_dict('records')}, merge=True)
    else:
        movies = st.session_state.added_movies_c
        movies.drop(movies[movies['id'] == id].index, inplace = True)
        st.session_state.added_movies_c = movies
        user_ref.set({'addedMoviesC': st.session_state.added_movies_c.to_dict('records')}, merge=True)
    
    
    
    
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def do_nothing():
    return True
    
# endregion -------------------- ------ ------------------------------     
    
    
# ----------------------- Login Success Message / Logout Button ----------------------                   
 
if st.session_state.logged_in:      
    with st.sidebar:
        login_msg_cols = st.columns([0.75,0.25])
        login_msg_cols[0].success('Welcome '+st.session_state.user)   
        login_msg_cols[1].write('')
        login_msg_cols[1].button('Logout', on_click=logout)
                    
# -----------------------                                       ----------------------   

# ----------- Setup page layout/containers ------------------

main_columns = st.columns([0.2,0.8,0.2])
with main_columns[1]:
    add_vertical_space(3)
    search_container = st.container()
    add_vertical_space(1)
    info_container = st.container()
    
search_container.markdown(f"<p style='text-align: left; font-size: 16px; color: black;'>👤Search Users</p>", unsafe_allow_html=True)
search = search_container.text_input('Search Users', label_visibility='collapsed')

if search:
    user_ref = st.session_state.db.collection('users').document(search)
    doc = user_ref.get()
    if doc.exists:
        user_info = doc.to_dict()
        added_movies_s = pd.DataFrame(user_info['addedMoviesS'])
        added_movies_a = pd.DataFrame(user_info['addedMoviesA'])
        added_movies_b = pd.DataFrame(user_info['addedMoviesB'])
        added_movies_c = pd.DataFrame(user_info['addedMoviesC'])
            
        tier_tabs = st.tabs(['S tier         ', 'A tier         ', 'B tier         ', 'C tier         '])
        for i,tab in enumerate(tier_tabs):
            if i == 0:
                tier = 's'
                added_movies = added_movies_s
            elif i == 1:
                tier = 'a'
                added_movies = added_movies_a
            elif i == 2:
                tier = 'b'
                added_movies = added_movies_b
            else:
                tier = 'c'
                added_movies = added_movies_c
            
            with tab:
                add_vertical_space(1)
                if added_movies.shape[0] > 0:
                    grid_container = st.container()   
                    with grid_container:    
                        grid_cols = st.columns(3)
                        for x in range(added_movies.shape[0]):
                            col = grid_cols[x%3]
                            with col:
                                with stylable_container(
                                    key="container_with_border",
                                    css_styles="""
                                        {
                                            border: 1px solid rgba(49, 51, 63, 0.2);
                                            border-radius: 0.5rem;
                                            padding: calc(1em - 1px)
                                            
                                        }
                                        """,
                                    ): 
                                        card_cols = st.columns([0.05,0.3,0.4,0.1,0.05])
                                        y = added_movies.iloc[x]
                                        with card_cols[1]:
                                            add_vertical_space(1)
                                            # card(
                                            #     title='',
                                            #     text='',
                                            #     image='https://image.tmdb.org/t/p/original/'+y.poster,
                                            #     styles={
                                            #                 "card": {
                                            #                     "width": "230px",
                                            #                     "height": "250px",
                                            #                     "border-radius": "10px",
                                            #                     "box-shadow": "0 0 0 0 rgba(0,0,0,0.5)",
                                            #                     "margin": "10",
                                            #                 },
                                            #                 "filter": {
                                            #                     "background-color": "rgba(0.0, 0.0, 0.0, 0.0)",
                                            #                 },
                                            #             },
                                            #     on_click=do_nothing
                                            # )
                                            st.image('https://image.tmdb.org/t/p/original/'+y.poster, width=120)
                                            
                                            
                                        
                                        left_details = {}
                                        left_details['title'] = y.title
                                        left_details['director'] = y.director
                                        left_details['lead'] = y.lead
                                        left_details['release_date'] = y.release_date
                                        left_details['date_reviewed'] = str(y.date_added)
                                        
                                        # with card_cols[2]:
                                        #     add_vertical_space(1)
                                        #     st.write(left_details)
                                        
                                        with card_cols[2]:
                                            add_vertical_space(1)
                                            st.markdown(f"<p style='text-align: left; color: black; font-size: 14px;'>Title: {y.title}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: left; color: black; font-size: 14px;'>Director: {y.director}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: left; color: black; font-size: 14px;'>Lead: {y.lead}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: left; color: black; font-size: 14px;'>Release Date: {y.release_date}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: left; color: black; font-size: 14px;'>Review Date: {y.date_added}</p>", unsafe_allow_html=True)
                                            
                                        card_cols[3].button('❌', key=y.id, on_click=remove_movie, args=[y.id, tier])
                                        
                                        add_vertical_space(1)