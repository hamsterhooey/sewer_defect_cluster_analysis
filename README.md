# Project Title

Sewer Defect Cluster Analysis

## Project Overview

In most previous studies on sewer deterioration, a single numeric grade is used to represent the condition of a pipe segment. These numeric grades provides insights into the level of deterioration of a pipe, and are thus a handy metric for planning maintenance activities. However, representing pipe deterioration with a single grade, leads to a loss of information, such as the location, density, and co-occurrence of defects – information which, when considered alongside contextual information of the pipe, can be crucial in determining their susceptibility to failure. According to previous studies, the pipe segment on the left and right of the images below, would both be considered to be equally deteriorated. However, we believe that pipe b has a higher likelihood of failure because:
(1) the defects, which are in close proximity could propagate and coalesce into more severe defects;
(2) multiple cracks and fractures increase the risk of void formation, due to soil entering the pipe. Voids over pipes are known to create sinkholes; and
(3) the pipe has a higher chance of collapse due to the existence of a localized region of weakness


![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%201.jpg)


### Extraction and annotation of images

Please see annotated_images.py. It runs a Tkinter-based tool to mark events in a video. Events represent the start and end of a particular feature appearing in the video. For instance, marking the start and end of an event which involves the camera making a turn.

Please see annotated_images.py. It runs a Tkinter-based tool to mark events in a video. Events represent the start and end of a particular feature appearing in the video. For instance, marking the start and end of an event which involves the camera making a turn.

Once a video has been marked, extract_images.py reads the marked events and extracts images between the marked time intervals. For instance if an event is marked at 10 seconds and 15 seconds, then extract_images.py can be used to extract multiple images in this time interval.

The extracted images are then labeled with bounding boxes using the LabelImg tool (github:Tzuatlin).

![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%201.jpg)

### Training a model to detect vanishing points and joints

We then use tensorflow object detection api to train a Faster R-CNN model. We make use of the numerous utils provided by tensorflow to accomplish this.

![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%202.jpg)

### Inference on videos to detect joint and vanishing points

We then run the inference script located in the "models" folder, to load the frozen tensorflow model and process frames of an input video.

![alt text](https://github.com/hamsterhooey/CCTV_Orientation_Recognition/blob/master/images/Step%203.jpg)

### Example Usage

```
python annotate_videos.py --media_db "data/video_databases/Media_Inspections.csv" --cond_db "data/video_databases/Conditions.csv" --video_path "data/video_files/3.MPG"
```
```
python extract_images.py --video_dir "data/video_files" --output_dir "data/extracted_labeled_images" --num_frames 10
```

### Prerequisites

Tested using opencv3.4.2

## Authors

* **Srinath Shiv Kumar** - [hamsterhooey](https://github.com/hamsterhooey)
