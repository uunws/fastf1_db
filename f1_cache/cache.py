import fastf1
import os

script_directory = os.path.dirname(os.path.abspath(__file__)) 
cache_path = os.path.join(script_directory, 'f1_cache') 

# Create cache directory if it doesn't exist
os.makedirs(cache_path, exist_ok=True)

fastf1.Cache.enable_cache(cache_path)