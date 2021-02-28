import streamlit as st
from streamlit.report_thread import get_report_ctx
import pandas as pd
import numpy as np
import csv
import base64

# EH: Exception handling

class SessionState(object):
    """
    # https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92#gistcomment-3484515
    """
    def __init__(self, **kwargs):
        """A new SessionState object.

        Parameters
        ----------
        **kwargs : any
            Default values for the session state.

        Example
        -------
        >>> session_state = SessionState(user_name='', favorite_color='black')
        >>> session_state.user_name = 'Mary'
        ''
        >>> session_state.favorite_color
        'black'

        """
        for key, val in kwargs.items():
            setattr(self, key, val)


@st.cache(allow_output_mutation=True)
def get_session(id, **kwargs):
    return SessionState(**kwargs)


def get(**kwargs):
    """Gets a SessionState object for the current session.

    Creates a new object if necessary.

    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.

    Example
    -------
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    ''
    >>> session_state.user_name = 'Mary'
    >>> session_state.favorite_color
    'black'

    Since you set user_name above, next time your script runs this will be the
    result:
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state.user_name
    'Mary'

    """
    ctx = get_report_ctx()
    id = ctx.session_id
    return get_session(id, **kwargs)


def download_link(object_to_download, download_filename, download_link_text):
    """
    # https://discuss.streamlit.io/t/heres-a-download-function-that-works-for-dataframes-and-txt/4052
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def main():
    html_temp = """ 
    <div style ="background-color:white;padding:10px"> 
    <h1 style ="color:black;text-align:center;">Random Data Generator App</h1> 
    </div> 
    """
    # s = get_session(np.random.randint(low=0, 
    #                                     high=10000000,
    #                                     size=1)) 
    
	

    st.markdown(html_temp, unsafe_allow_html = True)
    
    session_state = get(numerical_dict={}, categorical_dict={})
    st.sidebar.title("Data Configuration:")
    data_size = st.sidebar.number_input("Size of Data (N)", value=10, step=1, min_value=1, max_value=None)

    # EH: Duplicates are handled automatically because we are using dictionary. Verify for edge cases
    st.sidebar.subheader("Numerical Variables Configuration:")
    # st.sidebar.write("Enter range and data type")
    numerical_variable_name = st.sidebar.text_input("Numerical variable name", value="")
    variable_type = st.sidebar.selectbox("Variable type", ("Float", "Integer"))
    if variable_type == "Float":
        lower_bound = st.sidebar.number_input("Lower bound")
        higher_bound = st.sidebar.number_input("Higher bound")
    elif variable_type == "Integer":
        lower_bound = st.sidebar.number_input("Lower bound", value=0, step=1)
        higher_bound = st.sidebar.number_input("Higher bound", value=0, step=1)
    if st.sidebar.button("Add Numerical variable"):
        session_state.numerical_dict[numerical_variable_name] = {
            "lower_bound": lower_bound
            ,"higher_bound": higher_bound
            ,"variable_type": variable_type
        }
        st.sidebar.success("Added {} to numerical variables".format(numerical_variable_name))
        if session_state.numerical_dict:
            st.write("Summary of Numerical variables:")
            st.dataframe(pd.DataFrame.from_dict(session_state.numerical_dict, orient="index"))
        if session_state.categorical_dict:
            st.write("Summary of Categorical variables:")
            st.dataframe(pd.DataFrame.from_dict(session_state.categorical_dict, orient="index"))

    # EH: Formatting
    # EH: Duplicate names
    st.sidebar.subheader("Categorical Variables Configuration:")
    # st.sidebar.write("Write something here")
    categorical_variable_name = st.sidebar.text_input("Categorical variable name", value="")
    levels = st.sidebar.text_input("Input levels (Ex: Low,Med,High)", value="")
    if st.sidebar.button("Add Categorical variable"):
        session_state.categorical_dict[categorical_variable_name] = {
            "levels": levels
        }
        st.sidebar.success("Added {} to categorical variables".format(categorical_variable_name))
        if session_state.numerical_dict:
            st.write("Summary of Numerical variables:")
            st.dataframe(pd.DataFrame.from_dict(session_state.numerical_dict, orient="index"))
        if session_state.categorical_dict:
            st.write("Summary of Categorical variables:")
            st.dataframe(pd.DataFrame.from_dict(session_state.categorical_dict, orient="index"))

    # Prepare dataset

    # Prepare numerical dataset
    numerical_data_dict = {}
    for column in session_state.numerical_dict.keys():
        if session_state.numerical_dict[column]["variable_type"] == "Float":
            feature = np.random.uniform(low=session_state.numerical_dict[column]["lower_bound"], 
                                        high=session_state.numerical_dict[column]["higher_bound"],
                                        size=data_size)
        elif session_state.numerical_dict[column]["variable_type"] == "Integer":
            feature = np.random.randint(low=session_state.numerical_dict[column]["lower_bound"], 
                                        high=session_state.numerical_dict[column]["higher_bound"],
                                        size=data_size)
        numerical_data_dict[column] = feature

    # Prepare categorical dataset
    categorical_data_dict = {}
    for column in session_state.categorical_dict.keys():
        levels_list = np.unique([value.strip() for value in session_state.categorical_dict[column]["levels"].split(",")]).tolist()
        feature = np.random.choice(levels_list, size=data_size)
        categorical_data_dict[column] = feature  

    # Concatenate numerical and categorical data
    result_df = pd.concat(
        [pd.DataFrame(numerical_data_dict)
        ,pd.DataFrame(categorical_data_dict)],
        axis=1
    )
    
    if st.button("Generate"):
        if result_df.shape[0] == 0:
            st.write("Please input variable information")
        else:
            
            st.success("Random data is generated and saved to csv")
            st.write("Sample data is as shown below:")
            st.dataframe(result_df.sample(n=min(10, data_size)).reset_index(drop=True))
            # filename = st.text_input("Enter Sample Data Name", value="")
            # if st.button("Done"):
            tmp_download_link = download_link(result_df, 'Random_data.csv', 'Click here to download your data!')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
            
                
    if st.sidebar.button("Reset"):
        st.caching.clear_cache()


    

if __name__ == "__main__":
    main()
