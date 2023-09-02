import streamlit as st 
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
from custom_timeline import timeline

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.oauth2 import service_account

import pandas as pd
import base64
import json
import requests
from datetime import date

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
    .css-eczf16 {
        display:none
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
       
if 'page_mode' not in st.session_state.keys():
    st.session_state.page_mode = 'Ratings'
if 'timeline_data' not in st.session_state.keys():
    st.session_state.timeline_data = {
        'events': [],
    }

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
                    
                convert_to_timeline()
                
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
    
def convert_to_timeline():
    st.session_state.timeline_data['events'] = []

    for x in range(st.session_state.added_movies_s.shape[0]):
        y = st.session_state.added_movies_s.iloc[x]
        month, day, year =  y.date_added.split('/')
        entry = {"start_date": {}, "text": {}, "unique_id": None}
        entry['start_date']['year'] = year
        entry['start_date']['day'] = day
        entry['start_date']['month'] = month
        entry['text']['headline'] = y.title
        entry['unique_id'] = str(y.id)
        st.session_state.timeline_data['events'].append(entry)
        
    for x in range(st.session_state.added_movies_a.shape[0]):
        y = st.session_state.added_movies_a.iloc[x]
        month, day, year =  y.date_added.split('/')
        entry = {"start_date": {}, "text": {}, "unique_id": None}
        entry['start_date']['year'] = year
        entry['start_date']['day'] = day
        entry['start_date']['month'] = month
        entry['text']['headline'] = y.title
        entry['unique_id'] = str(y.id)
        st.session_state.timeline_data['events'].append(entry)
        
    for x in range(st.session_state.added_movies_b.shape[0]):
        y = st.session_state.added_movies_b.iloc[x]
        month, day, year =  y.date_added.split('/')
        entry = {"start_date": {}, "text": {}, "unique_id": None}
        entry['start_date']['year'] = year
        entry['start_date']['day'] = day
        entry['start_date']['month'] = month
        entry['text']['headline'] = y.title
        entry['unique_id'] = str(y.id)
        st.session_state.timeline_data['events'].append(entry)
        
    for x in range(st.session_state.added_movies_c.shape[0]):
        y = st.session_state.added_movies_c.iloc[x]
        month, day, year =  y.date_added.split('/')
        entry = {"start_date": {}, "text": {}, "unique_id": None}
        entry['start_date']['year'] = year
        entry['start_date']['day'] = day
        entry['start_date']['month'] = month
        entry['text']['headline'] = y.title
        entry['unique_id'] = str(y.id)
        st.session_state.timeline_data['events'].append(entry)
            

def handle_rating_button(id, tier, button):
    if tier != None and tier != button:
        user_ref = st.session_state.db.collection('users').document(st.session_state.user)
        ## remove movie in state belonging to ^ tier
        if tier == 'S':
            movies = st.session_state.added_movies_s
            movies.drop(movies[movies['id'] == id].index, inplace = True)
            st.session_state.added_movies_s = movies
            user_ref.set({'addedMoviesS': st.session_state.added_movies_s.to_dict('records')}, merge=True)
        elif tier == 'A':
            movies = st.session_state.added_movies_a
            movies.drop(movies[movies['id'] == id].index, inplace = True)
            st.session_state.added_movies_a = movies
            user_ref.set({'addedMoviesA': st.session_state.added_movies_a.to_dict('records')}, merge=True)
        elif tier == 'B':
            movies = st.session_state.added_movies_b
            movies.drop(movies[movies['id'] == id].index, inplace = True)
            st.session_state.added_movies_b = movies
            user_ref.set({'addedMoviesB': st.session_state.added_movies_b.to_dict('records')}, merge=True)
        elif tier == 'C':
            movies = st.session_state.added_movies_c
            movies.drop(movies[movies['id'] == id].index, inplace = True)
            st.session_state.added_movies_c = movies
            user_ref.set({'addedMoviesC': st.session_state.added_movies_c.to_dict('records')}, merge=True)   
        
    if button == 'S':
        st.session_state.id_match = st.session_state.added_movies_s.loc[st.session_state.added_movies_s['id'] == st.session_state.movie_details['id']]
        release = st.session_state.movie_details['release_date']
        review_date = date.today()
        user_ref = st.session_state.db.collection('users').document(st.session_state.user)
        if st.session_state.id_match.empty:
            df_new = pd.DataFrame.from_dict({'id': [st.session_state.movie_details['id']], 'title': [st.session_state.movie_details['title']], 'director': st.session_state.movie_details['director'], 'lead': st.session_state.movie_details['lead'], 'date_added': [review_date.strftime("%m/%d/%Y")], 'release_date': [release], 'poster': [st.session_state.movie_details['poster_path']]})
            st.session_state.added_movies_s = pd.concat([st.session_state.added_movies_s, df_new], ignore_index=True)
        else: 
            st.session_state.added_movies_s.loc[st.session_state.id_match.index,'date_added'] = review_date.strftime("%m/%d/%Y") 
        
        user_ref.set({'addedMoviesS': st.session_state.added_movies_s.to_dict('records')}, merge=True)
        st.session_state.movie_details = {} 
            
    if button == 'A':
        st.session_state.id_match = st.session_state.added_movies_a.loc[st.session_state.added_movies_a['id'] == st.session_state.movie_details['id']]
        release = st.session_state.movie_details['release_date']
        review_date = date.today()
        user_ref = st.session_state.db.collection('users').document(st.session_state.user)
        if st.session_state.id_match.empty:
            df_new = pd.DataFrame.from_dict({'id': [st.session_state.movie_details['id']], 'title': [st.session_state.movie_details['title']], 'director': st.session_state.movie_details['director'], 'lead': st.session_state.movie_details['lead'], 'date_added': [review_date.strftime("%m/%d/%Y")], 'release_date': [release], 'poster': [st.session_state.movie_details['poster_path']]})
            st.session_state.added_movies_a = pd.concat([st.session_state.added_movies_a, df_new], ignore_index=True)
        else: 
            st.session_state.added_movies_a.loc[st.session_state.id_match.index,'date_added'] = review_date.strftime("%m/%d/%Y")
            
        user_ref.set({'addedMoviesA': st.session_state.added_movies_a.to_dict('records')}, merge=True) 
        st.session_state.movie_details = {} 
            
    if button == 'B':
        st.session_state.id_match = st.session_state.added_movies_b.loc[st.session_state.added_movies_b['id'] == st.session_state.movie_details['id']]
        release = st.session_state.movie_details['release_date']
        review_date = date.today()
        user_ref = st.session_state.db.collection('users').document(st.session_state.user)
        if st.session_state.id_match.empty:
            df_new = pd.DataFrame.from_dict({'id': [st.session_state.movie_details['id']], 'title': [st.session_state.movie_details['title']], 'director': st.session_state.movie_details['director'], 'lead': st.session_state.movie_details['lead'], 'date_added': [review_date.strftime("%m/%d/%Y")], 'release_date': [release], 'poster': [st.session_state.movie_details['poster_path']]})
            st.session_state.added_movies_b = pd.concat([st.session_state.added_movies_b, df_new], ignore_index=True)
        else: 
            st.session_state.added_movies_b.loc[st.session_state.id_match.index,'date_added'] = review_date.strftime("%m/%d/%Y") 
            
        user_ref.set({'addedMoviesB': st.session_state.added_movies_b.to_dict('records')}, merge=True)    
        st.session_state.movie_details = {} 

    if button == 'C':
        st.session_state.id_match = st.session_state.added_movies_c.loc[st.session_state.added_movies_c['id'] == st.session_state.movie_details['id']]
        release = st.session_state.movie_details['release_date']
        review_date = date.today()
        user_ref = st.session_state.db.collection('users').document(st.session_state.user)
        if st.session_state.id_match.empty:
            df_new = pd.DataFrame.from_dict({'id': [st.session_state.movie_details['id']], 'title': [st.session_state.movie_details['title']], 'director': st.session_state.movie_details['director'], 'lead': st.session_state.movie_details['lead'], 'date_added': [review_date.strftime("%m/%d/%Y")], 'release_date': [release], 'poster': [st.session_state.movie_details['poster_path']]})
            st.session_state.added_movies_c = pd.concat([st.session_state.added_movies_c, df_new], ignore_index=True)
        else: 
            st.session_state.added_movies_c.loc[st.session_state.id_match.index,'date_added'] = review_date.strftime("%m/%d/%Y")

        user_ref.set({'addedMoviesC': st.session_state.added_movies_c.to_dict('records')}, merge=True)
        st.session_state.movie_details = {} 
    
    convert_to_timeline()
    change_page_mode()  
    
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
        
    convert_to_timeline()
    
    
def search_movies(search):
    if search != '':
        # get page 1 of search query as json response
        search_url = 'https://api.themoviedb.org/3/search/movie'
        url = search_url+f'?query={search}&include_adult=false&language=en-US&page={st.session_state.page_num}'
        response = requests.get(url, headers=headers).json()
        
        # store movie ids and posters for display
        results = []
        for movie in response['results']:
            if movie['poster_path'] is None:
                continue
            x = [movie['id'], movie['title'], movie['release_date'], movie['poster_path'], movie['overview']]
            results.append(x)
        st.session_state.search_results = results
        
def sort_results():
    selectbox_contents = []
    for x in st.session_state.search_results:
        l = x[:-2]
        l.append(x[0])
        l = l[1:]
        selectbox_contents.append(l)
    return selectbox_contents

        
def get_movie_details(selection,pp,overview):
    details_url = 'https://api.themoviedb.org/3/movie/'
    url = details_url+f'{selection[2]}/credits'
    info = {}
    movie = requests.get(url, headers=headers).json()
    info['id'] = selection[2]
    info['director'] = [x for x in movie['crew'] if x['job'] == 'Director'][0]['name']
    info['lead'] = movie['cast'][0]['name']
    info['title'] = selection[0]
    info['release_date'] = selection[1]
    info['poster_path'] = pp
    info['overview'] = overview
    st.session_state.movie_details = info    
    
    
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

def change_page_mode():
    if st.session_state.page_mode == 'Ratings':
        st.session_state.page_mode = 'Review'
    else:
        st.session_state.page_mode = 'Ratings'
    
# endregion -------------------- ------ ------------------------------     
    
    
# ----------------------- Login Success Message / Logout Button ----------------------                   
 
if st.session_state.logged_in:      
    with st.sidebar:
        login_msg_cols = st.columns([0.75,0.25])
        login_msg_cols[0].success('Welcome '+st.session_state.user)   
        login_msg_cols[1].write('')
        login_msg_cols[1].button('Logout', on_click=logout)
                    
# -----------------------                                       ----------------------   

if st.session_state.logged_in: 
    if st.session_state.page_mode == 'Ratings':
        
        with st.sidebar:
            add_vertical_space(10)
            with stylable_container(
            key="centering_container",
            css_styles="""
                {
                    text-align: center;
                }
                """,
            ): 
                with stylable_container(
                    key="green_button",
                    css_styles="""
                        button {
                            background-color: white;
                            color: black;
                            border-radius: 10px;
                            padding: 16px 50px;
                        }
                        """,
                    ):
                    st.button("Add Movie ➕", on_click=change_page_mode)
        
        add_vertical_space(3)
        
        # --------------- timeline ----------------------
        
        options = {
            "initial_zoom": "1",
        }
        timeline(st.session_state.timeline_data, height=230, additional_options=options)
        
        
        # ------------ tier tabs ------------------------ 
                    
        add_vertical_space(2)
        list_tabs = ['S tier', 'A tier', 'B tier', 'C tier']
        whitespace = 10
        tier_tabs = st.tabs([t.center(whitespace,"\u2001") for t in list_tabs])
        for i,tab in enumerate(tier_tabs):
            
            if i == 0:
                tier = 's'
                added_movies = st.session_state.added_movies_s
            elif i == 1:
                tier = 'a'
                added_movies = st.session_state.added_movies_a
            elif i == 2:
                tier = 'b'
                added_movies = st.session_state.added_movies_b
            else:
                tier = 'c'
                added_movies = st.session_state.added_movies_c
            
            with tab:
                add_vertical_space(1)
                if added_movies.shape[0] > 0:
                    grid_container = st.container()   
                    with grid_container:    
                        grid_cols = st.columns(4)
                        for x in range(added_movies.shape[0]):
                            col = grid_cols[x%4]
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
                                        y = added_movies.iloc[x]
                                        card_cols = st.columns([0.05,0.45,0.45,0.05])
                                        button_containers = st.columns([0.4,0.6])
                                        with card_cols[1]:
                                            
                                            add_vertical_space(1)
                                            st.image('https://image.tmdb.org/t/p/original/'+y.poster, caption=y.title, use_column_width=True)
                                            add_vertical_space(1)
                                        
                                        with card_cols[2]:
                                            add_vertical_space(1)
                                            st.markdown(f"<p style='text-align: center; color: black; font-size: 14px;'>Title:     {y.title}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: center; color: black; font-size: 14px;'>Director:     {y.director}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: center; color: black; font-size: 14px;'>Lead:      {y.lead}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: center; color: black; font-size: 14px;'>Release Date:      {y.release_date}</p>", unsafe_allow_html=True)
                                            st.markdown(f"<p style='text-align: center; color: black; font-size: 14px;'>Review Date:     {y.date_added}</p>", unsafe_allow_html=True)
                                        
                                        button_containers[1].button('❌', key=y.id, on_click=remove_movie, args=[y.id, tier])
                else:
                    add_vertical_space(20)
                    st.markdown(f"<p style='text-align: center; color: black; font-size: 16px;'>No movies here.</p>", unsafe_allow_html=True)
    
    else:
        add_vertical_space(2)
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                }
                """,
            ): 
            main_columns = st.columns([0.2,0.8,0.2])
            with main_columns[1]:
                search_container = st.container()
                info_container = st.container()
                buttons_container = st.container()
                
            with search_container:
                add_vertical_space(1)
                st.markdown(f"<p style='text-align: left; font-size: 16px; color: black;'>🔍Search Movies</p>", unsafe_allow_html=True)
                search = search_container.text_input('Search Movies', label_visibility='collapsed')
                    
            if search:
                add_vertical_space(1)
                search_movies(search)
                sorted_list = sort_results()
                selection = search_container.selectbox('', sorted_list, label_visibility='collapsed')
                if selection:
                    for x in st.session_state.search_results:
                        if x[0] == selection[2]:
                            pp = x[3]
                            overview = x[4]
                    get_movie_details(selection, pp, overview)
                    movie = st.session_state.movie_details
                    
                    ## check for matches 
                    tier = None
                    rev_date = None
                    
                    id_match = st.session_state.added_movies_s.loc[st.session_state.added_movies_s['id'] == st.session_state.movie_details['id']]
                    if not id_match.empty:
                        tier = 'S'
                        rev_date = st.session_state.added_movies_s.loc[id_match.index].date_added.values[0]   
                    id_match = st.session_state.added_movies_a.loc[st.session_state.added_movies_a['id'] == st.session_state.movie_details['id']]
                    if not id_match.empty:
                        tier = 'A'
                        rev_date = st.session_state.added_movies_a.loc[id_match.index].date_added.values[0]   
                    id_match = st.session_state.added_movies_b.loc[st.session_state.added_movies_b['id'] == st.session_state.movie_details['id']]
                    if not id_match.empty:
                        tier = 'B'
                        rev_date = st.session_state.added_movies_b.loc[id_match.index].date_added.values[0]   
                    id_match = st.session_state.added_movies_c.loc[st.session_state.added_movies_c['id'] == st.session_state.movie_details['id']]
                    if not id_match.empty:
                        tier = 'C'
                        rev_date = st.session_state.added_movies_c.loc[id_match.index].date_added.values[0]   
                    
                    with info_container:
                                    
                        with stylable_container(
                            key="container_with_border",
                            css_styles="""
                                {
                                    border: 1px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                }
                                """,
                            ): 
                                    
                                if tier != None and rev_date != None:
                                    st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Last reviewed as {tier} tier on {rev_date}</h3>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>You have not yet rated this movie.</h3>", unsafe_allow_html=True)
                                
                                add_vertical_space(1)   
                                info_cols = st.columns([0.13,0.37,0.4,0.1])
                                with info_cols[1]:
                                    add_vertical_space(1)
                                    # card(
                                    #     title='', 
                                    #     text=movie['title'],
                                    #     image='https://image.tmdb.org/t/p/original/'+movie['poster_path'], 
                                    #     styles={
                                    #         "card": {
                                    #             "width": "275px",
                                    #             "height": "250px",
                                    #             "border-radius": "10px",
                                    #             "box-shadow": "0 0 0 0 rgba(0,0,0,0.5)",
                                    #             "margin": "10"
                                            
                                    #         },
                                    #         "text": {
                                    #             "font-family": "sans-serif",
                                    #         },
                                    #         "filter": {
                                    #             "background-color": "rgba(0.0, 0.0, 0.0, 0.0)",
                                    #         },
                                    #     },
                                    #     on_click=do_nothing
                                    #     )
                                    st.image('https://image.tmdb.org/t/p/original/'+movie['poster_path'],  width=225)
                                        
                                keys = ['title', 'director', 'lead', 'release_date']
                                display = {}
                                for key, value in st.session_state.movie_details.items():
                                    if key in keys:
                                        display[key] = value 
                                with info_cols[2]:
                                    add_vertical_space(1)
                                    st.write(display)
                                    
                                add_vertical_space(2)
                            
                    with buttons_container:
                        st.markdown(f"<h3 style='text-align: center; color: black; font-size: 20px;'>Rate this movie</h3>", unsafe_allow_html=True)
                        form_columns = st.columns(4)

                        with stylable_container(
                            key="container",
                            css_styles="""
                                {
                                    text-align: center;
                                    padding: 0, 10, 0, 10;
                                }
                                """,
                            ):
                            s_button = form_columns[0].button('S tier', use_container_width=True, on_click=handle_rating_button, args=[st.session_state.movie_details['id'], tier, 'S'])
                            a_button = form_columns[1].button('A tier', use_container_width=True, on_click=handle_rating_button, args=[st.session_state.movie_details['id'], tier, 'A'])
                            b_button = form_columns[2].button('B tier', use_container_width=True, on_click=handle_rating_button, args=[st.session_state.movie_details['id'], tier, 'B'])
                            c_button = form_columns[3].button('C tier', use_container_width=True, on_click=handle_rating_button, args=[st.session_state.movie_details['id'], tier, 'C'])
                            add_vertical_space(1)  
                        
                        
                        
            else:
                add_vertical_space(45)
                                           
else:
    add_vertical_space(3)
    bin_str = get_base64_of_bin_file('./resources/login_image.png')
    with stylable_container(
        key="background_container",
        css_styles="""
            {
                border: 1px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                background-image: url("data:image/png;base64,%s");
                background-size: contain;
            }

            """ % bin_str,
        ): 
        add_vertical_space(19)
        st.markdown(f"<h3 style='text-align: center; color: black;'>Login to start rating movies.</h3>", unsafe_allow_html=True)
        add_vertical_space(21)
            
            
    with st.sidebar:
        login_tab, sign_up_tab = st.tabs(['Login', 'Sign-Up'])
        with login_tab:     
            with stylable_container(
                key="container",
                css_styles="""
                    {
                        text-align: center;
                        padding: 0, 10, 0, 10;
                    }
                    """,
            ):
                with st.form('login'):
                    user = st.text_input('Username', key='user_input')
                    password = st.text_input('Password', key='pass_input')
                    login = st.form_submit_button('Login', on_click=authenticate)
        with sign_up_tab:
            with stylable_container(
                key="container",
                css_styles="""
                    {
                        text-align: center;
                        padding: 0, 10, 0, 10;
                    }
                    """,
            ):
                with st.form('signup'):
                    email = st.text_input('Email', key='email_input')
                    user = st.text_input('Username', key='s_user_input')
                    password = st.text_input('Password', key='s_pass_input')
                    signup = st.form_submit_button('Sign-Up', on_click=sign_up)
    