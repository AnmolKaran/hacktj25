from videodb import connect
from videodb import play_stream
import os
from videodb import SceneExtractionType
from videodb import SearchType, IndexType


os.environ["VIDEO_DB_API_KEY"] = "sk-Ug9TvC77uoKqegQxdlrs0acB9tMcFHfPJvsFa1-xdHA"
os.environ["OPENAI_API_KEY"] = "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"
conn = connect()
coll = conn.get_collection()

video = coll.upload(url="https://www.youtube.com/watch?v=libKVRa01L8")
stream = video.generate_stream()

video.index_spoken_words()

# Index scene content
index_id = video.index_scenes(
    extraction_type=SceneExtractionType.time_based,
    extraction_config={"time": 2, "select_frames": ["first", "last"]},
    prompt="Describe the scene in detail",
)
spoken_query = "Show me where the narrator discusses the formation of the solar system"
# Perform the search using the spoken query
spoken_results = video.search(
    query=spoken_query,
    index_type=IndexType.spoken_word,
    search_type=SearchType.semantic,
)

# View the results
print(spoken_results)