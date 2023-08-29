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

</style>

""", unsafe_allow_html=True)

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="my-movie-ranking")

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64); tutukito/koolkidsteel8@gmail.com', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOTJiYmNiY2IxNWM4ZWM2MDQxZTE3NmE3ZGJkY2NhYSIsInN1YiI6IjY0ZDg0NDg5ZDEwMGI2MDBhZGExOTE0YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.KDRfub8-zkbIjM0AcIcf82PnvilKNhwzjMDbBi4A9Wo'}

if 'page_num' not in st.session_state.keys():
    st.session_state.page_num = 1
if 'search_results' not in st.session_state.keys():
    st.session_state.search_results = []
if 'movie_details' not in st.session_state.keys():
    st.session_state.movie_details = {}
    
if 'added_movies' not in st.session_state.keys():
    st.session_state.added_movies = pd.DataFrame(columns=['id', 'title', 'content', 'presentation', 'score', 'date_added']) 
if 'added_movies_user' not in st.session_state.keys():
    st.session_state.added_movies_user = None
    
if 'logged_in' not in st.session_state.keys():
    st.session_state.logged_in = False
if 'user' not in st.session_state.keys():
    st.session_state.user = None

# endregion -------------------- ------ ------------------------------
    
# region --------------------  functions  ------------------------------

def sign_up():
    if st.session_state.s_user_input and st.session_state.s_pass_input and st.session_state.email_input:
        user_ref = db.collection('users')
        query_ref = user_ref.where(filter=FieldFilter("email", "==", st.session_state.email_input))
        if len(query_ref.get()) > 0:
            st.sidebar.warning('email already in use')
            return
        doc = user_ref.document(st.session_state.s_user_input).get()
        if doc.exists:
            st.sidebar.warning('this username is already taken')
            return
        else:
            data = {'addedMovies': [], 'email': st.session_state.email_input, 'pass': st.session_state.s_pass_input}
            db.collection("users").document(st.session_state.s_user_input).set(data)     
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
        user_ref = db.collection('users').document(st.session_state.user_input)
        doc = user_ref.get()
        if doc.exists:
            user_info = doc.to_dict()
            if st.session_state.pass_input == user_info['pass']:
                st.session_state.user = st.session_state.user_input
                st.session_state.added_movies_user = st.session_state.user_input
                st.session_state.logged_in = True
                st.session_state.user_input = None
                st.session_state.pass_input = None
                added_movies = user_info['addedMovies']
                if len(added_movies) > 0:
                    st.session_state.added_movies = pd.DataFrame(added_movies)
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
    
    
def remove_movie(id):
    movies = st.session_state.added_movies
    movies.drop(movies[movies['id'] == id].index, inplace = True)
    st.session_state.added_movies = movies
    user_ref = db.collection('users').document(st.session_state.user)
    user_ref.set({'addedMovies': st.session_state.added_movies.to_dict('records')}, merge=True)
    
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
    if st.session_state.added_movies.shape[0] > 0:
        grid_container = st.container()   
        with grid_container:    
            grid_cols = st.columns([0.05,0.45,0.45,0.05])
            st.session_state.added_movies = st.session_state.added_movies.sort_values(by=['score'], ascending=False)
            for x in range(st.session_state.added_movies.shape[0]):
                col = grid_cols[(x%2)+1]
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
                            card_cols = st.columns([0.45,0.45,0.1])
                            y = st.session_state.added_movies.iloc[x]
                            with card_cols[0]:
                                add_vertical_space(1)
                                card(
                                    title='',
                                    text='',
                                    image='https://image.tmdb.org/t/p/original/'+y.poster,
                                    styles={
                                                "card": {
                                                    "width": "230px",
                                                    "height": "250px",
                                                    "border-radius": "10px",
                                                    "box-shadow": "0 0 0 0 rgba(0,0,0,0.5)",
                                                    "margin": "10",
                                                },
                                                "filter": {
                                                    "background-color": "rgba(0.0, 0.0, 0.0, 0.0)",
                                                },
                                            },
                                )
                                
                            
                            left_details = {}
                            left_details['ranking'] = x+1
                            left_details['score'] = y.score
                            left_details['title'] = y.title
                            left_details['release_date'] = y.release_date
                            left_details['date_reviewed'] = str(y.date_added)
                            
                            with card_cols[1]:
                                st.write(left_details)
                            
                            # with card_cols[1]:
                            #     add_vertical_space(2)
                            #     st.write('ranking: ' + str(x+1))
                            #     st.write('score: ' + str(y.score))
                            #     st.write('ranking: ' + y.title)
                            #     st.write('ranking: ' + y.release_date)
                            #     st.write('ranking: ' + str(y.date_added))
                                
                            card_cols[2].button('❌', key=y.id, on_click=remove_movie, args=[y.id])
                                           
    else:
        st.markdown(f"<h3 style='text-align: center; color: black;'>You have not reviewed any movies.</h3>", unsafe_allow_html=True)
else:
    add_vertical_space(2)
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
    