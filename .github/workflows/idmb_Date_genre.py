import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Replace with your actual API key
api_key = "a85857d8cbbbaa62a0e6b5b845cdb2e9"

# Validate date format
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # Check if the date matches the YYYY-MM-DD format
        return True
    except ValueError:
        return False

# Function to get genres
def get_genres():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    genres_data = response.json()
    return genres_data['genres']

# Function to fetch movies by genre
def fetch_movies_by_genre(genre_id, start_date, end_date):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}&with_genres={genre_id}&page=1"
    
    # Initialize a list to hold all movies
    all_movies = []
    
    try:
        # Fetch all movies with pagination
        page = 1
        while True:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an error for 4xx/5xx status codes
            data = response.json()
            
            if 'results' in data:
                # Add movies from the current page to the all_movies list
                all_movies.extend(data['results'])

                # Check if there are more pages
                if data['page'] < data['total_pages']:
                    page += 1
                    url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}&with_genres={genre_id}&page={page}"
                else:
                    break
            else:
                messagebox.showinfo("No Movies", f"No movies found for genre {genre_id} between {start_date} and {end_date}.")
                return []

        return all_movies

    except requests.exceptions.HTTPError as http_err:
        messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        messagebox.showerror("Request Error", f"Request error occurred: {req_err}")
    except Exception as err:
        messagebox.showerror("Error", f"Other error occurred: {err}")
    
    return []

# Function to handle the fetching and saving process
def fetch_and_save_movies():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    
    # Validate date format
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        messagebox.showerror("Invalid Date", "Please enter valid dates in YYYY-MM-DD format.")
        return
    
    genre_name = genre_combobox.get()
    if not genre_name:
        messagebox.showerror("No Genre", "Please select a genre.")
        return
    
    # Get genre ID from the genre list
    genre_id = next(genre['id'] for genre in genres if genre['name'] == genre_name)

    # Fetch movies by the selected genre and date range
    movies = fetch_movies_by_genre(genre_id, start_date, end_date)

    if movies:
        # Generate a file name based on genre and date range
        file_name = f"{genre_name}_{start_date}_to_{end_date}.txt"
        
        # Save movie data to file
        with open(file_name, 'w', encoding='utf-8') as file:
            for movie in movies:
                movie_id = movie['id']
                title = movie['title']
                release_date = movie['release_date']

                # Fetch IMDb ID and TMDb ID (external IDs)
                external_ids_url = f"https://api.themoviedb.org/3/movie/{movie_id}/external_ids?api_key={api_key}"
                external_ids_response = requests.get(external_ids_url)
                external_ids_data = external_ids_response.json()

                imdb_id = external_ids_data.get('imdb_id', 'N/A')  # Default to 'N/A' if IMDb ID is not available

                # Write the Movie Info to the file
                file.write(f"TMDb ID: {movie_id} | Title: {title} | Release Date: {release_date} | IMDb ID: {imdb_id}\n")
        
        messagebox.showinfo("File Saved", f"Movies for genre '{genre_name}' between {start_date} and {end_date} have been saved to {file_name}")

# Create the main window
root = tk.Tk()
root.title("Movie Fetcher")

# Fetch genres for the ComboBox
genres = get_genres()

# Set up the GUI layout
tk.Label(root, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
start_date_entry = tk.Entry(root)
start_date_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10)
end_date_entry = tk.Entry(root)
end_date_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Select Genre:").grid(row=2, column=0, padx=10, pady=10)
genre_combobox = ttk.Combobox(root, values=[genre['name'] for genre in genres])
genre_combobox.grid(row=2, column=1, padx=10, pady=10)

# Add button to fetch and save movies
fetch_button = tk.Button(root, text="Fetch Movies and Save", command=fetch_and_save_movies)
fetch_button.grid(row=3, column=0, columnspan=2, padx=10, pady=20)

# Start the Tkinter event loop
root.mainloop()
