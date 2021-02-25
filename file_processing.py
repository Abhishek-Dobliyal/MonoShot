# Required Imports
import cv2 # pip install opencv-python
from cv2 import dnn_superres # pip install opencv-contrib-python
from moviepy.editor import * # pip install moviepy
import moviepy.video.fx.all as vfx
from PIL import Image, ImageEnhance # pip install pillow
import numpy as np # pip install numpy
import pytesseract as pyt # pip install pytesseract

# VideoProcessor class for all processing related methods
class FileProcessor:
    def __init__(self, file):
        self.__file = file.name # Fetch the location of the file for processing
    
    def get_duration(self):
        ''' Get the duration of video file in 
            seconds '''
        video = cv2.VideoCapture(self.__file)
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT) 
        fps = int(video.get(cv2.CAP_PROP_FPS)) 
        duration = int(frames / fps)

        return duration

    def get_dimensions(self):
        ''' Get the dimesnions of file '''
        file = cv2.VideoCapture(self.__file)
        width, height = file.get(3), file.get(4)

        # Return true if the file uploaded has dimensions btw 480p and 1080p
        return (int(width) in range(852, 1921) and int(height) in range(480, 1081)) \
               or (int(height) in range(852, 1921) and int(width) in range(480, 1081))
        
    def generate_shot(self, output_path, slowmo=False, 
                       timelapse=False, gif=False, 
                       boomerang=(False, None, None)):
        ''' Generates specified shot of the 
        video file '''
        if slowmo or timelapse:
            video = cv2.VideoCapture(self.__file)
            FW, FH = int(video.get(3)), int(video.get(4))
            FOUR_CC = cv2.VideoWriter_fourcc(*"AVC1")

            if slowmo:
                FPS = 5.5
                output = cv2.VideoWriter(f"./{output_path}/slow_motion.mp4", FOUR_CC, FPS, (FW, FH))
                while video.isOpened():
                    ret, frame = video.read()
                    if not ret:
                        break
                    output.write(frame)

            elif timelapse:
                FPS = 30
                count, speed = 0, 10
                frames = []
                output = cv2.VideoWriter(f"./{output_path}/timelapse.mp4", FOUR_CC, FPS, (FW, FH))

                while video.isOpened():
                    ret, frame = video.read()
                    if not ret:
                        break

                    if count % speed == 0:
                        frames.append(frame)

                    count += 1

                for frame in frames:
                    output.write(frame)
        
            video.release()
            output.release()

        elif gif:
            video_file = VideoFileClip(self.__file).resize(0.6)
            video_file.write_gif(f"./{output_path}/sample.gif")
        
        elif boomerang[0]:
            start, end = boomerang[1], boomerang[2]
            video_file = VideoFileClip(self.__file).resize(0.6)

            clip = video_file.subclip(start, end) # Get subclip from the video file
            clip = clip.fx(vfx.crop, x1=115, x2=399, y1=0, y2=288)

            speed_clip = clip.speedx(2)
            reversed_speed_clip = speed_clip.fx(vfx.time_mirror)

            final = concatenate_videoclips([speed_clip, reversed_speed_clip]) # Merge the clips
            final.to_gif(f"./{output_path}/boomerang.gif", fps=25)

    def enhanced_img(self, output_path, timestamp, brightness_lvl,
                    sharpness_lvl, contrast_level, color_level):
        ''' Extar image from a specified
        video time stamp and generate an enhanced 
        version of it'''
        TEMP_IMG_PATH = "./temp_files/original_enhanced_img.png"
        video = cv2.VideoCapture(self.__file)
        video.set(cv2.CAP_PROP_POS_MSEC, timestamp)
        video.set(3, 1920)
        video.set(4, 1080)
        _, frame = video.read()
        cv2.imwrite(TEMP_IMG_PATH, frame)
        video.release()

        # Normalize image to reduce noise
        img = cv2.imread(TEMP_IMG_PATH, cv2.IMREAD_UNCHANGED)
        normalized_img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX) 

        # Apply final enhancements according to parameters
        rgb_img = cv2.cvtColor(normalized_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)

        if brightness_lvl != 1.0:
            pil_img = ImageEnhance.Brightness(pil_img).enhance(brightness_lvl)
        elif sharpness_lvl != 1.0:
            pil_img = ImageEnhance.Sharpness(pil_img).enhance(sharpness_lvl)
        elif contrast_level != 1.0:
            pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast_level)
        elif color_level != 1.0:
            pil_img = ImageEnhance.Color(pil_img).enhance(color_level)

        pil_img.save(f"{output_path}/enhanced_img.png")

    def enhance_resolution(self, output_path):
        ''' Enhance the resolution of the image
        using Super Resolution technique '''
        MODEL_PATH = "./assets/FSRCNN_x4.pb" 

        img = cv2.imread(self.__file)

        # Apply DNN Super Resolution technique using pre trained model (in our case FSRCNN model)
        sr = dnn_superres.DnnSuperResImpl_create()
        sr.readModel(MODEL_PATH)
        sr.setModel("fsrcnn", 4)

        final_img = sr.upsample(img)

        final_img = cv2.fastNlMeansDenoisingColored(final_img, None, 10, 10, 7, 15) # Remove Noise
        cv2.imwrite(f"./{output_path}/enhanced_resolution.png", final_img)

    def apply_filter(self, output_path, filter=None):
        ''' Apply specified filter to the image '''
        img = cv2.imread(self.__file, cv2.IMREAD_UNCHANGED)

        if filter == "Pencil Sketch":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inverted_img = cv2.bitwise_not(gray)
            smooth_img = cv2.GaussianBlur(inverted_img, (21,21), sigmaX=0, sigmaY=0)

            final_img = cv2.divide(gray, 255 - smooth_img, scale=256)
            cv2.imwrite(f"./{output_path}/pencil_sketch.png", final_img)
        
        elif filter == "Faded":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(f"./{output_path}/faded.png", gray)
        
        elif filter == "Water Colored":
            final_img = cv2.stylization(img, sigma_s=60, sigma_r=0.07)
            cv2.imwrite(f"./{output_path}/water_colored.png", final_img)
        
        elif filter == "Cartoonify":
            smooth_img = cv2.bilateralFilter(img, 10, 250, 250)

            # Work on edge lines
            gray = cv2.cvtColor(smooth_img, cv2.COLOR_BGR2GRAY)
            img_blur = cv2.medianBlur(gray, 5)
            img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY, 7, 2)

            # Multiply the original and edge lined img
            final_img = cv2.bitwise_and(smooth_img, smooth_img, mask=img_edge)
            cv2.imwrite(f"./{output_path}/cartoonified.png", final_img)
        
        elif filter == "Document":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY, 151, 10)
            final_img = cv2.medianBlur(adaptive_thresh, 3)
            
            cv2.imwrite(f"./{output_path}/document.png", final_img)
        
        elif filter == "Vigenette":
            rows, cols = img.shape[:2]

            # Generating vignette mask using Gaussian kernels
            kernel_x = cv2.getGaussianKernel(cols,450)
            kernel_y = cv2.getGaussianKernel(rows,450)
            kernel = kernel_y * kernel_x.T
            kernel = kernel / kernel.max()

            final_img = np.copy(img)
            final_img[:, :, :] = 0
            final_img[:, :, 0] = img[:, :, 0] * kernel
            final_img[:, :, 1] = img[:, :, 1] * kernel
            final_img[:, :, 2] = img[:, :, 2] * kernel

            cv2.imwrite(f"./{output_path}/vigenette.png", final_img)
        
        elif filter == "Phantom":
            # Kernel to apply the effect
            kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])
            final_img = cv2.filter2D(img, -1, kernel) # Apply a Filter with given kernel

            cv2.imwrite(f"./{output_path}/phantom.png", final_img)
        
        elif filter == "Negative":
            final_img = cv2.bitwise_not(img)
            cv2.imwrite(f"./{output_path}/negative.png", final_img)

    def extract_txt(self):
        ''' Extract text from images '''
        img = cv2.imread(self.__file)

        # Convert image into Grayscale and then apply threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

        # Kernel to detect sentences (around rectangle)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

        # Dilation to create enlarged image of same shape
        dilated = cv2.dilate(threshold, kernel, 1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL,  
                                      cv2.CHAIN_APPROX_NONE) 

        text = ""
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt) # Get the coordinated where txt is located 

            cropped_txt_img = img[y:y+h, x:x+w] 

            text += pyt.image_to_string(cropped_txt_img)
        
        # " \n\x0c" is a string that is returned when the img does not contain any text 
        if text !=  " \n\x0c":
            return text