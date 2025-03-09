import torch
import numpy as np
# from IPython.display import Image
import torch
import av
import imageio
from transformers import XCLIPProcessor, XCLIPModel
from openai import OpenAI
from PIL import Image
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import os

model_name = "microsoft/xclip-base-patch16-zero-shot"
processor = XCLIPProcessor.from_pretrained(model_name)
model = XCLIPModel.from_pretrained(model_name)

if(torch.cuda.is_available()):
    model.to("cuda:0")




np.random.seed(0)
transformation_prompt = """
Divide the following query into two distinct parts: one for spoken content and one for visual content. The spoken content should refer to any narration, dialogue, or verbal explanations and The visual content should refer to any images, videos, or graphical representations. Format the response strictly as:\nSpoken: <spoken_query>\nVisual: <visual_query>\n\nQuery: {query}
"""
OPENAI_API_KEY = "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"

# Initialize OpenAI client
def download_video(url, output_path):
    """
    Download a video from a given url and save it to the output path.

    Parameters:
    url (str): The url of the video to download.
    output_path (str): The path to save the video to.

    Returns:
    dict: A dictionary containing the metadata of the video.
    """
    yt = YouTube(url)
    metadata = {"Author": yt.author, "Title": yt.title, "Views": yt.views}
    yt.streams.get_highest_resolution().download(
        output_path=output_path, filename="input_vid.mp4"
    )
    return metadata


def video_to_images(video_path, output_folder):
    """
    Convert a video to a sequence of images and save them to the output folder.

    Parameters:
    video_path (str): The path to the video file.
    output_folder (str): The path to the folder to save the images to.

    """
    clip = VideoFileClip(video_path)
    clip.write_images_sequence(
        os.path.join(output_folder, "frame%04d.png"), fps=0.2
    )


def video_to_audio(video_path, output_audio_path):
    """
    Convert a video to audio and save it to the output path.

    Parameters:
    video_path (str): The path to the video file.
    output_audio_path (str): The path to save the audio to.

    """
    clip = VideoFileClip(video_path)
    audio = clip.audio
    audio.write_audiofile(output_audio_path)


def audio_to_text(audio_path):
    """
    Convert audio to text using the SpeechRecognition library.

    Parameters:
    audio_path (str): The path to the audio file.

    Returns:
    test (str): The text recognized from the audio.

    """
    recognizer = sr.Recognizer()
    audio = sr.AudioFile(audio_path)

    with audio as source:
        # Record the audio data
        audio_data = recognizer.record(source)

        try:
            # Recognize the speech
            text = recognizer.recognize_whisper(audio_data)
        except sr.UnknownValueError:
            print("Speech recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from service; {e}")

    return text
def divide_query(query):
    client = OpenAI(api_key = OPENAI_API_KEY)
    # Use the OpenAI client to create a chat completion with a structured prompt
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": transformation_prompt.format(query=query)}
        ],
    )

    message = response.choices[0].message.content
    divided_query = message.strip().split("\n")
    spoken_query = divided_query[0].replace("Spoken:", "").strip()
    visual_query = divided_query[1].replace("Visual:", "").strip()

    return spoken_query, visual_query

def unnormalize_img(img):
    """Un-normalizes the image pixels."""
    img = (img * np.std(img)) + np.mean(img)
    img = (img * 255).astype("uint8")
    return img.clip(0, 255)


def create_gif(video_tensor, filename="sample.gif"):
    """Prepares a GIF from a video tensor.

    The video tiensor is expected to have the following shape:
    (num_frames, num_channels, height, width).
    """
    frames = []
    for video_frame in video_tensor:
        frame_unnormalized = unnormalize_img(video_frame.permute(1, 2, 0).numpy())
        frames.append(frame_unnormalized)
    kargs = {"duration": 0.25}
    imageio.mimsave(filename, frames, "GIF", **kargs)
    return filename


def display_gif(video_tensor, gif_name="sample.gif"):
    """Prepares and displays a GIF from a video tensor."""
    video_tensor = video_tensor.permute(1, 0, 2, 3)
    gif_filename = create_gif(video_tensor, gif_name)
    return Image(filename=gif_filename)


def read_video_pyav(container, indices):
    '''
    Decode the video with PyAV decoder.
    Args:
        container (`av.container.input.InputContainer`): PyAV container.
        indices (`List[int]`): List of frame indices to decode.
    Returns:
        result (np.ndarray): np array of decoded frames of shape (num_frames, height, width, 3).
    '''
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            # Convert frame to RGB and ensure correct shape
            rgb_frame = frame.to_ndarray(format="rgb24")  # Ensure RGB format
            frames.append(rgb_frame)
    
    frames = np.stack(frames)
    
    # Ensure shape is (num_frames, height, width, 3)
    if frames.shape[-1] != 3:
        raise ValueError(f"Unexpected video frame shape: {frames.shape}, expected (num_frames, height, width, 3)")

    return frames



def sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    converted_len = int(clip_len * frame_sample_rate)
    end_idx = np.random.randint(converted_len, seg_len)
    start_idx = end_idx - converted_len
    indices = np.linspace(start_idx, end_idx, num=clip_len)
    indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)
    return indices

def classify(video_path, labels):
    container = av.open(video_path)
    
    # Sample 32 frames
    indices = sample_frame_indices(clip_len=32, frame_sample_rate=1, seg_len=container.streams.video[0].frames)
    video = read_video_pyav(container, indices)
    
    # Convert numpy array to list of PIL images (optional, but can help)
    video_frames = [Image.fromarray(frame) for frame in video]

    # Ensure `videos` input is a proper list
    inputs = processor(
        text=labels, 
        videos=video_frames, 
        return_tensors="pt", 
        padding=True,  # Ensures uniform text input length
        truncation=True  # Truncates long text inputs to avoid mismatches
    )
    
    if torch.cuda.is_available():
        inputs.to("cuda:0")

    # Forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    probs = outputs.logits_per_video.softmax(dim=1)
    return labels[probs.argmax()], probs.max()




# Ensure your OpenAI API key is set
os.environ["OPENAI_API_KEY"] = "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"

def find_antonym(word_or_phrase: str) -> str:
    """
    Finds the antonym of a given word or phrase using an LLM via LangChain.
    
    Args:
        word_or_phrase (str): The word or phrase for which to find the antonym.
    
    Returns:
        str: The antonym of the given word or phrase.
    """
    llm = ChatOpenAI(model="gpt-4", temperature=0)  

    # Different prompts for single words vs phrases
    if " " in word_or_phrase:
        prompt = f"Provide a phrase that conveys the opposite meaning of: '{word_or_phrase}'."
    else:
        prompt = f"Provide a single-word antonym for: '{word_or_phrase}'."

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return response.content.strip()


def combine_with_opposite(phrases):
  combined = []
  for word in phrases:
    combined.append([word, find_antonym(word)])
  return combined

def true_classification(video_path, phrases, groups):

  flagged = []
  for idx, val in enumerate(groups):
    x = classify(video_path, val)
    print(x)
    if float(x.data[0][0])>0.75:
      flagged.append(phrases[idx])
  return flagged
