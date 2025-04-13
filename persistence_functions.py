
# Functions for audio file persistence
def load_paper_audio_files():
    """Load paper_audio_files from disk if they exist"""
    global paper_audio_files
    
    # Try to load from JSON file first (human-readable)
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'paper_audio_files.json')
    pickle_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'paper_audio_files.pickle')
    
    try:
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                # Convert string keys back to original format
                for key, value in loaded_data.items():
                    paper_audio_files[key] = value
                print(f"Loaded {len(paper_audio_files)} audio mappings from JSON file")
        elif os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as f:
                loaded_data = pickle.load(f)
                paper_audio_files.update(loaded_data)
                print(f"Loaded {len(paper_audio_files)} audio mappings from pickle file")
    except Exception as e:
        print(f"Error loading paper_audio_files: {str(e)}")

def save_paper_audio_files():
    """Save paper_audio_files to disk for persistence"""
    try:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'paper_audio_files.json')
        pickle_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'paper_audio_files.pickle')
        
        # First try JSON format for readability
        try:
            # Ensure instance directory exists
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(paper_audio_files, f, ensure_ascii=False, default=str)
            print(f"Saved {len(paper_audio_files)} audio mappings to JSON file")
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}, falling back to pickle")
            # Fallback to pickle format
            with open(pickle_path, 'wb') as f:
                pickle.dump(paper_audio_files, f)
            print(f"Saved {len(paper_audio_files)} audio mappings to pickle file")
    except Exception as e:
        print(f"Error saving paper_audio_files: {str(e)}")
