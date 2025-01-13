import os
import requests
from tqdm import tqdm

def download_model(url, destination):
    """
    Download the model file with a progress bar.
    """
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as file, tqdm(
        desc=destination,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

if __name__ == "__main__":
    model_url = "https://llama3-2-lightweight.llamameta.net/*?Policy=eyJTdGF0ZW1lbnQiOlt7InVuaXF1ZV9oYXNoIjoicGI2dzRkbzBnbXk4OG8yYmQ4aHZ2NjYyIiwiUmVzb3VyY2UiOiJodHRwczpcL1wvbGxhbWEzLTItbGlnaHR3ZWlnaHQubGxhbWFtZXRhLm5ldFwvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTczNjI4MTA4MH19fV19&Signature=JOE9Ilh-KDfNfIeCzmeaQX0dpZR1QPzlpB281%7EJ7kL%7EbKIkZt8P85eE8rTKUwUl2OrNEakaQmuj5l6qno2uiXqeJni-vLoGYCGU9tWjghdlHyt543glMMuapsQP1yKmwnsEHlCLfcNAD6DhMzkH9WJ2dt2fYo9IpP9itk6z3BMOOXnab25QCSzazDvKtCr%7EKTFWCdXRbgu7S2lIU9QhWhHW10u08O1OBfoaRsXda%7Eek0WBH8bMKILyPqjzIb451leJFATXMRVyyPgmLZSv4HQGhz6g1VambPWsCloGCitewCNr72wcNeM4bqix9eb5d1-YWWGipfMl07ce9KM7Godw__&Key-Pair-Id=K15QRJLYKIFSLZ&Download-Request-ID=1615211626538062"  # Replace with your model URL
    model_path = os.path.join('llama', 'llama-2-7b-chat.gguf')
    
    if not os.path.exists('llama'):
        os.makedirs('llama')
    
    download_model(model_url, model_path) 