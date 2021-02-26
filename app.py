# Required Imports
import streamlit as st # pip install streamlit
from file_processing import FileProcessor
import tempfile
import os
import shutil
import time

# Helper Functions
def get_file_data(file):
    ''' Writes the uploaded file data
    to a temporary file for processing'''
    if not os.path.isdir("./temp_files"):
        os.mkdir("./temp_files")

    tempfile.tempdir = "temp_files" # Set the directory where all temp files will be stores
    temp_file = tempfile.NamedTemporaryFile(suffix="file_for_processing")
    temp_file.write(file.read())

    return temp_file

def display_progress_bar():
    ''' Displays a progress bar to visualize
    the completion of a function '''
    processing_txt = st.markdown("#### Processing, Please wait...")
    bar = st.progress(0)
    for percent in range(100):
        time.sleep(0.05)
        bar.progress(percent)

    bar.empty()
    processing_txt.empty()

def display_msg(msg, msg_type=0):
    ''' Display message according to the
    type 
    1 -> Success Message
    0 -> Info Message
    -1 -> Error Message
    '''
    msg_widget = st.empty()
    
    if msg_type == 1:
        msg_widget = st.success(msg)
        time.sleep(3)
        msg_widget.empty()
    
    elif msg_type == -1:
        msg_widget = st.error(msg)
        time.sleep(3)
        msg_widget.empty()
    
    elif msg_type == 0:
        msg_widget = st.info(msg)
        time.sleep(3)
        msg_widget.empty()

def get_file_details(processed_file_path, processed_file_details, file_extension):
    ''' Dispalys the basic details of the file
    inside an expander widget '''
    info_expander = st.beta_expander("Output Section")
    with info_expander:
        processed_col, file = st.beta_columns(2)
        processed_col.write(processed_file_details)

        if file_extension in ("mov", "mp4", "avi"):
            file.video(processed_file_path)
        else:
            file.image(processed_file_path)

def display_processed_file(processed_file_path, processed_files):
    ''' Displays the processed file in web app '''
    if not processed_files:
        display_msg("No files processed yet.", -1)

    elif len(processed_files) == 1:
        file = processed_files[0]
        processed_filename, processed_file_ext = os.path.basename(processed_file_path + file).split('.')
        processed_file_details = {
            "File Name": processed_filename,
            "File Type": processed_file_ext,
            "File Size": str(round(os.path.getsize(processed_file_path + file) / 1e6, 2)) + " MB"
        }

        if processed_file_ext in ("mov", "mp4", "avi"):
            get_file_details(processed_file_path + file, processed_file_details, 
                            processed_file_ext)
        else:
            get_file_details(processed_file_path + file, processed_file_details, 
                            processed_file_ext)
    
    else:
        display_msg("You can only process and download a single file at a time", 0)
    
    shutil.rmtree(processed_file_path)

def display_info_sections():
    ''' Displays the instructions and about section '''
    help_expander = st.beta_expander("Instructions")
    about_expander = st.beta_expander("About")

    instructions = '''
            * **Choose or Drag N Drop** a file to upload. For a video file, the duration must not exceed 
            the 30 seconds mark.

            * Once uploaded, select the enhacements you would like to apply from the sidebar.

            * Click on the **Generate** button and wait for the processing to complete.

            * Once completed, click on the **Proceed to Download** button to generate the output.

            * Wait for the processing to complete **(notice the RUNNING status on the top right hand corner)**.
            Once completed, expand the **Output Section** section to view the output.

            * If satisfied with the results:
                - If the output is an image file then right click on the file and 
                select the **Save as** option to download the output ( This applies to
                GIFs and Boomerangs as well ).
                
                - If it is a video file then click on the **Three dots** present at 
                the bottom right corner inside the video player and select **Download**.

    '''

    about = '''
            Made By  <span style="color:seagreen">**Abhishek Dobliyal**</span> :smile: 
            [![GitHub Abhishek-Dobliyal](https://img.shields.io/github/followers/Abhishek-Dobliyal?label=follow&style=social)](https://github.com/Abhishek-Dobliyal)
            [![Linkedin: Abhishek Dobliyal]
            (https://img.shields.io/badge/-AbhishekDobliyal-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/abhishek-dobliyal-4474061b7/)]
            (https://www.linkedin.com/in/abhishek-dobliyal-4474061b7) 

            #### Modules Utilized:
            - <a style="text-decoration: none;" href="http://streamlit.io/" target="blank_"> Streamlit </a>
            - <a style="text-decoration: none;" href="https://opencv.org/releases/" target="blank_"> OpenCV </a>
            - <a style="text-decoration: none;" href="https://zulko.github.io/moviepy/" target="blank_"> MoviePy </a>
            - <a style="text-decoration: none;" href="https://pillow.readthedocs.io/en/3.0.x/index.html" target="blank_"> Pillow </a>
            - <a style="text-decoration: none;" href="https://numpy.org/" target="blank_"> NumPy </a>

            #### Hope You Like It :blush:
    '''
    with help_expander: # Instructions
        help_expander.markdown(instructions, unsafe_allow_html=True)

    with about_expander: # About
        about_expander.markdown(about, unsafe_allow_html=True)

# Main App
def main():
    ''' The main Web app '''
    # Set Page name and favicon
    ICON = "./assets/favicon.png"
    st.set_page_config(page_title="MonoShot", page_icon=ICON)

    # Title
    TITLE_STYLE = '''
                border: 3px solid #9ab7d6;
                border-radius: 15px;
                text-align: center;
                background: rgb(220, 235, 237);
                color: white;
                font-family: Futura, sans-serif;
                color: pink;
                text-shadow: #000 0px 0px 1px;
            '''
    title = f'''
            <div style="{TITLE_STYLE}">
                <h1> MONOSHOT </h1>
            </div>
            '''
    st.markdown(title, unsafe_allow_html=True) # Render the HTML/CSS

    # Header
    HEADER = "Just a single shot that's all it takes."
    st.subheader(HEADER)

    # File Upload and Selections
    PROCESSED_DATA_PATH = "./processed_data/"

    uploaded_file = st.file_uploader("Upload your file here:",
                                    type=[".mp4", ".avi", ".mov", ".jpeg", ".jpg", ".png"])
    if uploaded_file:
        file_data = get_file_data(uploaded_file)
        processor = FileProcessor(file_data) # Processor object for applying diff. methods to the media file

        if uploaded_file.type in ("video/mp4", "video/mov", "video/avi"):
            if not os.path.isdir(PROCESSED_DATA_PATH):
                os.mkdir(PROCESSED_DATA_PATH)

            video_duration = processor.get_duration()
            has_required_dim = processor.get_dimensions()

            if video_duration > 30:
                display_msg("Oops! Video too long to be processed!", -1)
            
            elif not has_required_dim:
                display_msg("Oops! Allowed Resolutions are: 360p, 480p, 720p and 1080p", -1)

            else:
                # SideBar Widgets 
                select_options = ["Enhance Image", "Generate Shot"]
                select_output = st.sidebar.selectbox("Select Enhancement:", select_options)

                if select_output:
                    time.sleep(1.5)
                    if select_output == "Enhance Image":
                        time_stamp = st.sidebar.slider("Choose the time stamp (in seconds)", 
                                                    min_value=1, max_value=video_duration, 
                                                    step=1)
                        brightness_lvl = st.sidebar.slider("Brightness:", 
                                                    min_value=0.0, max_value=2.0, 
                                                    step=0.2, value=1.0)
                        sharpness_lvl = st.sidebar.slider("Sharpness:", 
                                                    min_value=0.0, max_value=2.0, 
                                                    step=0.2, value=1.0)
                        contrast_lvl = st.sidebar.slider("Contrast:", 
                                                    min_value=0.0, max_value=2.0, 
                                                    step=0.2, value=1.0)
                        color_lvl = st.sidebar.slider("Color:", 
                                                    min_value=0.0, max_value=2.0, 
                                                    step=0.2, value=1.0)

                        if st.sidebar.button("Generate"):
                            processor.enhanced_img(PROCESSED_DATA_PATH, time_stamp*1000, # Timestamp should be in milliseconds
                                                    brightness_lvl, sharpness_lvl, 
                                                    contrast_lvl, color_lvl) 
                            display_progress_bar()
                            display_msg("Enhanced Image has been successfully generated.", 1)

                    elif select_output == "Generate Shot":
                        display_msg("NOTE: It may take a while to generate a shot.", 0)

                        shot_options = ["SlowMo", "TimeLapse", "GIF", "Boomerang"]
                        shot = st.sidebar.selectbox("Select Shot:", shot_options)

                        if shot == "SlowMo" and st.sidebar.button("Generate"):
                            processor.generate_shot(PROCESSED_DATA_PATH, slowmo=True)
                            display_progress_bar()
                            display_msg("SlowMo has been successfully generated.", 1)
                        
                        elif shot == "TimeLapse" and st.sidebar.button("Generate"):
                            processor.generate_shot(PROCESSED_DATA_PATH, timelapse=True)
                            display_progress_bar()
                            display_msg("TimeLapse has been successfully generated.", 1)
                        
                        elif shot == "GIF" and st.sidebar.button("Generate"):
                            processor.generate_shot(PROCESSED_DATA_PATH, gif=True)
                            display_progress_bar()
                            display_msg("GIF has been successfully generated.", 1)
                        
                        elif shot == "Boomerang":
                            start_time = st.sidebar.slider("Choose the start time (in seconds):", 
                                                    min_value=1, max_value=video_duration, 
                                                    step=1)
                            end_time = st.sidebar.slider("Choose the end time (in seconds):", 
                                                    min_value=start_time + 2, max_value=video_duration, 
                                                    step=1)

                            if st.sidebar.button("Generate"):
                                processor.generate_shot(PROCESSED_DATA_PATH, 
                                                       boomerang=(True, start_time, end_time))
                                display_progress_bar()
                                display_msg("Boomerang has been successfully generated.", 1)

                else:
                    display_msg("Please select atleast a single option to proceed.", 0)

        else:
            if not os.path.isdir(PROCESSED_DATA_PATH):
                os.mkdir(PROCESSED_DATA_PATH)

            select_options = ["Enhance Resolution", "Apply Filter", "Extract Text"]
            select_output = st.sidebar.selectbox("Select Enhancement:", select_options)

            if select_output:
                time.sleep(1.5)
                if select_output == "Enhance Resolution":

                    if st.sidebar.button("Generate"):
                        display_msg("Please wait. It may take a while to enhance the resolution...", 0)
                        processor.enhance_resolution(PROCESSED_DATA_PATH)
                        display_progress_bar()
                        display_msg("Enhanced Resolution Image has been successfully generated.", 1)
                
                elif select_output == "Apply Filter":
                    select_options = ["Pencil Sketch", "Water Colored", "Faded", "Document",
                                     "Cartoonify", "Vigenette", "Phantom", "Negative"]
                    select_output = st.sidebar.selectbox("Select a filter:", select_options)

                    if st.sidebar.button("Generate"):
                        processor.apply_filter(PROCESSED_DATA_PATH, filter=select_output)
                        display_progress_bar()
                        display_msg("Filter has been successfully applied.", 1)

                elif select_output == "Extract Text":
                    if st.sidebar.button("Fetch Text"):
                        txt = processor.extract_txt()
                    
                        if txt:
                            display_msg("Text extraction successful.", 1)
                            text_expander = st.beta_expander("Output Section")
                            with text_expander:
                                st.text("*" * 70)
                                st.write(txt)
                                st.text("*" * 70)
                        else:
                            display_msg("Failed to extract text!", -1)

            else:
                display_msg("Please select atleast a single option to proceed.", 0)

        file_data.close() # Delete the temp file after all the operations.
        shutil.rmtree("./temp_files") 

        helper_widget = st.empty()
        processed_files = os.listdir(PROCESSED_DATA_PATH)

        if processed_files:
            if helper_widget.button("Proceed to Download"):
                    display_processed_file(PROCESSED_DATA_PATH, processed_files)

    display_info_sections()

if __name__ == '__main__':
    main()