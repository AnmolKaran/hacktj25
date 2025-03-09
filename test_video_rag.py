from videodb import connect
from videodb import play_stream
import os
from videodb import SceneExtractionType
from videodb import SearchType, IndexType


os.environ["VIDEO_DB_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""
conn = connect()
coll = conn.get_collection()

video = coll.upload(url="https://www.youtube.com/watch?v=libKVRa01L8")
stream = video.generate_stream()

video.index_spoken_words()

index_id = video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 2, "select_frames": ["first", "last"]},
    prompt="Describe the scene in detail",
)
spoken_query = "Show me where the narrator discusses the formation of the solar system"

spoken_results = video.search(
    query=spoken_query,
    index_type=IndexType.spoken_word,
    search_type=SearchType.semantic,
)

print(spoken_results)