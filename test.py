import streamlit as st 
from __init__ import timeline

# s = st.session_state.added_movies_s
# for x in range(s.shape[0]):
#     y = st.session_state.added_movies_s.iloc[x]
#     st.write(y.date_added)
# [0]['date_added']
# m, d, y = s.split('/')
# st.write(m,d,y)

data = {
    "title": {
        "media": {
          "url": "",
          "caption": " <a target=\"_blank\" href=''>credits</a>",
          "credit": ""
        },
        "text": {
          "headline": "Welcome to<br>Streamlit Timeline",
          "text": "<p>A Streamlit Timeline component by integrating TimelineJS from Knightlab</p>"
        }
    },
    "events": [
      {
        "media": {
          "url": "https://vimeo.com/143407878",
          "caption": "How to Use TimelineJS (<a target=\"_blank\" href='https://timeline.knightlab.com/'>credits</a>)"
        },
        "start_date": {
          "year": "2016",
          "month":"1"
        },
        "text": {
          "headline": "TimelineJS<br>Easy-to-make, beautiful timelines.",
          "text": "<p>TimelineJS is a populair tool from Knightlab. It has been used by more than 250,000 people to tell stories seen hundreds of millions of times, and is available in more than sixty languages. </p>"
        }
      },
      {
        "media": {
          "url": "https://www.youtube.com/watch?v=CmSKVW1v0xM",
          "caption": "Streamlit Components (<a target=\"_blank\" href='https://streamlit.io/'>credits</a>)"
        },
        "start_date": {
          "year": "2020",
          "month":"7",
          "day":"13"
        },
        "text": {
          "headline": "Streamlit Components<br>version 0.63.0",
          "text": "Streamlit lets you turn data scripts into sharable web apps in minutes, not weeks. It's all Python, open-source, and free! And once you've created an app you can use our free sharing platform to deploy, manage, and share your app with the world."
        }
      },
      {
        "media": {
          "url": "https://github.com/innerdoc/streamlit-timeline/raw/main/component-logo.png",
          "caption": "github/innerdoc (<a target=\"_blank\" href='https://www.github.com/innerdoc/'>credits</a>)"
        },
        "start_date": {
          "year": "2021",
          "month":"2"
        },
        "text": {
          "headline": "Streamlit TimelineJS component",
          "text": "Started with a demo on https://www.innerdoc.com/nlp-timeline/ . <br>Then made a <a href='https://github.com/innerdoc/streamlit-timeline'>Streamlit component</a> of it. <br>Then made a <a href='https://pypi.org/project/streamlit-timeline/'>PyPi package</a> for it."
        }
      }
    ]
}

data1 = st.session_state.timeline_data
options = {
    "initial_zoom": "1",
    "width": "500",
}
timeline(data, height=250, additional_options=options)
# st.markdown(f"""<iframe src="https://cdn.knightlab.com/libs/timeline3/latest/embed/index.html?source=1xuY4upIooEeszZ_lCmeNx24eSFWe0rHe9ZdqH2xqVNk&font=Default&lang=en&initial_zoom=2&height=100%" width="100%" frameborder="0"></iframe>
#                                 """, unsafe_allow_html=True)