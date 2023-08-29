import streamlit as st 
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_extras.switch_page_button import switch_page
from google.cloud.firestore_v1.base_query import FieldFilter

from datetime import date
from google.cloud import firestore
import pandas as pd
import requests 
import base64

# region --------------------  config  ------------------------------

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
    button[title="View fullscreen"]{
        visibility: hidden;
    }
        section.main > div:has(~ footer ) {
        padding-bottom: 5px;
    }

</style>

""", unsafe_allow_html=True)

db = firestore.Client.from_service_account_json("firestore-key.json")
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64); tutukito/koolkidsteel8@gmail.com', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxOTJiYmNiY2IxNWM4ZWM2MDQxZTE3NmE3ZGJkY2NhYSIsInN1YiI6IjY0ZDg0NDg5ZDEwMGI2MDBhZGExOTE0YiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.KDRfub8-zkbIjM0AcIcf82PnvilKNhwzjMDbBi4A9Wo'}

if 'page_num' not in st.session_state.keys():
    st.session_state.page_num = 1
if 'search_results' not in st.session_state.keys():
    st.session_state.search_results = []
if 'movie_details' not in st.session_state.keys():
    st.session_state.movie_details = {}
    
if 'added_movies' not in st.session_state.keys():
    st.session_state.added_movies = pd.DataFrame(columns=['id', 'title', 'content', 'presentation', 'score', 'date_added']) 
if 'id_match' not in st.session_state.keys():
    st.session_state.id_match = None
    
if 'logged_in' not in st.session_state.keys():
    st.session_state.logged_in = False
if 'user' not in st.session_state.keys():
    st.session_state.user = None


# endregion -------------------- ------ ------------------------------

# region -------------------- functions ------------------------------

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
            x = [movie['id'], movie['title'], movie['release_date'], movie['poster_path']]
            results.append(x)
        st.session_state.search_results = results
        
def get_movie_details(selection,pp):
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
    st.session_state.movie_details = info


#     if st.session_state.movie_details != {}:
    # with info_container.container():
    #     sb_cols = st.columns([0.05,0.45,0.45,0.05])
    #     sb_cols[1].image('https://image.tmdb.org/t/p/original/'+st.session_state.movie_details['poster_path'], use_column_width=True, caption=st.session_state.movie_details['title'])
        # keys = ['director', 'lead', 'release_date']
        # display = {}
        # for key, value in st.session_state.movie_details.items():
        #     if key in keys:
        #         display[key] = value 

        # sb_cols[2].write(display)
        
        # add_vertical_space(2)
        # sb_cols1 = st.columns([0.3,0.4,0.3])
        # st.session_state.id_match = st.session_state.added_movies.loc[st.session_state.added_movies['id'] == st.session_state.movie_details['id']]
        # if st.session_state.id_match.empty:
        #     rate = sb_cols1[1].button('⭐Review', use_container_width=True)
        # else:
        #     rate = sb_cols1[1].button('✏️Edit', use_container_width=True)
        # if rate:
        #     st.write('pressed')


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
                st.session_state.logged_in = True
                st.session_state.user_input = None
                st.session_state.pass_input = None
                st.session_state.added_movies = pd.DataFrame(user_info['addedMovies'])
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


# ----------- Setup page layout/containers ------------------

main_columns = st.columns([0.2,0.8,0.2])
with main_columns[1]:
    search_container = st.container()
    add_vertical_space(2)
    info_container = st.container()
    form_container = st.container()
    
# ---------- Page Contents ---------------------------------

if st.session_state.logged_in:
    with search_container:
        st.markdown(f"<p style='text-align: left; font-size: 16px; color: black;'>🔍Search Movies</p>", unsafe_allow_html=True)
        search = search_container.text_input('Search Movies', label_visibility='collapsed')
        if search:
            search_movies(search)
            selectbox_contents = []
            for x in st.session_state.search_results:
                l = x[:-1]
                l.append(x[0])
                l = l[1:]
                selectbox_contents.append(l)
            selection = selectbox('', selectbox_contents)
            if selection:
                for x in st.session_state.search_results:
                    if x[0] == selection[2]:
                        pp = x[3]
                get_movie_details(selection, pp)
                movie = st.session_state.movie_details
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
                        info_cols = st.columns(2)
                        with info_cols[0]:
                            card(
                                title='', 
                                text=movie['title'],
                                image='https://image.tmdb.org/t/p/original/'+movie['poster_path'], 
                                styles={
                                    "card": {
                                        "width": "275px",
                                        "height": "250px",
                                        "border-radius": "10px",
                                        "box-shadow": "0 0 0 0 rgba(0,0,0,0.5)",
                                        "margin": "10"
                                    
                                    },
                                    "text": {
                                        "font-family": "sans-serif",
                                    },
                                    "filter": {
                                        "background-color": "rgba(0.0, 0.0, 0.0, 0.0)",
                                    },
                                },
                                )
                        keys = ['title', 'director', 'lead', 'release_date']
                        display = {}
                        for key, value in st.session_state.movie_details.items():
                            if key in keys:
                                display[key] = value 
                        with info_cols[1]:
                            add_vertical_space(3)
                            st.write(display)
            
                with form_container:
                    with st.form('Rating'):
                        form_columns = st.columns([ 0.25, 0.7, 0.05])
                        with form_columns[0]:
                            add_vertical_space(1)
                            st.markdown(f"<p style='text-align: center; font-size: 15px; color: black;'>Content</p>", unsafe_allow_html=True)
                            add_vertical_space(2)
                            st.markdown(f"<p style='text-align: center; font-size: 15px; color: black;'>Presentation</p>", unsafe_allow_html=True)
                        with form_columns[1]:
                            content = st.slider('Content', 0, 100, label_visibility='collapsed')
                            add_vertical_space(1)
                            presentation = st.slider('Presentation', 0, 100, label_visibility='collapsed')
                        with stylable_container(
                            key="container",
                            css_styles="""
                                {
                                    text-align: center;
                                    padding: 0, 10, 0, 10;
                                }
                                """,
                            ):
                            submit = st.form_submit_button('➕ ADD')
                
                if submit:
                    st.session_state.id_match = st.session_state.added_movies.loc[st.session_state.added_movies['id'] == st.session_state.movie_details['id']]
                    score = round((content*0.45)+(presentation*0.55), 2)
                    release = st.session_state.movie_details['release_date']
                    review_date = date.today()
                    if st.session_state.id_match.empty:
                        df_new = pd.DataFrame.from_dict({'id': [st.session_state.movie_details['id']], 'title': [st.session_state.movie_details['title']], 'content': [content], 'presentation': [presentation], 'score': [score], 'date_added': [review_date.strftime("%m/%d/%Y")], 'release_date': [release], 'poster': [st.session_state.movie_details['poster_path']]})
                        st.session_state.added_movies = pd.concat([st.session_state.added_movies, df_new], ignore_index=True)
                    else:
                        st.session_state.added_movies.loc[st.session_state.id_match.index,'content'] = content
                        st.session_state.added_movies.loc[st.session_state.id_match.index,'presentation'] = presentation
                        st.session_state.added_movies.loc[st.session_state.id_match.index,'score'] = score  
                        st.session_state.added_movies.loc[st.session_state.id_match.index,'review_date'] = review_date   
                    
                    user_ref = db.collection('users').document(st.session_state.user)
                    user_ref.set({'addedMovies': st.session_state.added_movies.to_dict('records')}, merge=True)
                    st.session_state.movie_details = {} 
                    switch_page('home')
    
else:
    
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