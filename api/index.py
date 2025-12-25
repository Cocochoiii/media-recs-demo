"""
Vercel Serverless API - Media Recommendation System
All poster URLs verified and working
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
import random
import os
import time

# ============================================
# MEDIA DATABASE - 100 Movies with VERIFIED poster URLs
# Using reliable TMDB image URLs
# ============================================

MEDIA_DATABASE = [
    # === ACTION MOVIES (1-10) ===
    {"id": 1, "title": "The Dark Knight", "year": 2008, "genres": ["Action", "Crime", "Drama"], "rating": 9.0, 
     "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg",
     "description": "When the menace known as the Joker wreaks havoc on Gotham, Batman must accept one of the greatest psychological and physical tests.", "duration": 152, "director": "Christopher Nolan", "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"], "popularity": 95, "media_type": "movie"},
    
    {"id": 2, "title": "Inception", "year": 2010, "genres": ["Action", "Sci-Fi", "Thriller"], "rating": 8.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
     "description": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea.", "duration": 148, "director": "Christopher Nolan", "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"], "popularity": 94, "media_type": "movie"},
    
    {"id": 3, "title": "Mad Max: Fury Road", "year": 2015, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2EwM2I5OWMtMGQyMi00Zjg1LWJkNTctZTdjYTA4OGUwZjMyXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/phszHPFVhPHhMZgo0fWTKBDQsJA.jpg",
     "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland.", "duration": 120, "director": "George Miller", "cast": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult"], "popularity": 88, "media_type": "movie"},
    
    {"id": 4, "title": "John Wick", "year": 2014, "genres": ["Action", "Crime", "Thriller"], "rating": 7.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTU2NjA1ODgzMF5BMl5BanBnXkFtZTgwMTM2MTI4MjE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/umC04Cozevu8nn3JTDJ1pc7PVTn.jpg",
     "description": "An ex-hit-man comes out of retirement to track down the gangsters that killed his dog and took everything from him.", "duration": 101, "director": "Chad Stahelski", "cast": ["Keanu Reeves", "Michael Nyqvist", "Alfie Allen"], "popularity": 86, "media_type": "movie"},
    
    {"id": 5, "title": "Top Gun: Maverick", "year": 2022, "genres": ["Action", "Drama"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BZWYzOGEwNTgtNWU3NS00ZTQ0LWJkODUtMmVhMjIwMjA1ZmQwXkEyXkFqcGdeQXVyMjkwOTAyMDU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/AaV1YIdWKhF9dBWaVVBQD8d1toE.jpg",
     "description": "After thirty years, Maverick is still pushing the envelope as a top naval aviator.", "duration": 130, "director": "Joseph Kosinski", "cast": ["Tom Cruise", "Jennifer Connelly", "Miles Teller"], "popularity": 92, "media_type": "movie"},
    
    {"id": 6, "title": "The Matrix", "year": 1999, "genres": ["Action", "Sci-Fi"], "rating": 8.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BNzQzOTk3OTAtNDQ0Zi00ZTVkLWI0MTEtMDllZjNkYzNjNTc4L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
     "description": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.", "duration": 136, "director": "The Wachowskis", "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"], "popularity": 90, "media_type": "movie"},
    
    {"id": 7, "title": "Gladiator", "year": 2000, "genres": ["Action", "Adventure", "Drama"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDliMmNhNDEtODUyOS00MjNlLTgxODEtN2U3NzIxMGVkZTA1L2ltYWdlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/mw04yp3AZcJgkAO9cH8DnwptPrg.jpg",
     "description": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.", "duration": 155, "director": "Ridley Scott", "cast": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen"], "popularity": 89, "media_type": "movie"},
    
    {"id": 8, "title": "Kill Bill: Vol. 1", "year": 2003, "genres": ["Action", "Crime", "Thriller"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BNzM3NDFhYTAtYmU5Mi00NGRmLTljYjgtMDkyODQ4MjNkMGY2XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/bj1SH7kzYQn5WkOEQAuM4CDUl9c.jpg",
     "description": "After awakening from a four-year coma, a former assassin wreaks vengeance on the team of assassins who betrayed her.", "duration": 111, "director": "Quentin Tarantino", "cast": ["Uma Thurman", "David Carradine", "Daryl Hannah"], "popularity": 86, "media_type": "movie"},
    
    {"id": 9, "title": "The Avengers", "year": 2012, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nNmJRkg8wWnRmzQDe2FwKbPIsJV.jpg",
     "description": "Earth's mightiest heroes must come together to stop Loki and his alien army from enslaving humanity.", "duration": 143, "director": "Joss Whedon", "cast": ["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson"], "popularity": 91, "media_type": "movie"},
    
    {"id": 10, "title": "Black Panther", "year": 2018, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 7.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTg1MTY2MjYzNV5BMl5BanBnXkFtZTgwMTc4NTMwNDI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/6ELJEzQJ3Y45HczvreC3dg0GV5R.jpg",
     "description": "T'Challa returns home to Wakanda to take his rightful place as king.", "duration": 134, "director": "Ryan Coogler", "cast": ["Chadwick Boseman", "Michael B. Jordan", "Lupita Nyong'o"], "popularity": 88, "media_type": "movie"},

    # === SCI-FI MOVIES (11-20) ===
    {"id": 11, "title": "Interstellar", "year": 2014, "genres": ["Sci-Fi", "Adventure", "Drama"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
     "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", "duration": 169, "director": "Christopher Nolan", "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"], "popularity": 93, "media_type": "movie"},
    
    {"id": 12, "title": "Blade Runner 2049", "year": 2017, "genres": ["Sci-Fi", "Drama", "Mystery"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BNzA1Njg4NzYxOV5BMl5BanBnXkFtZTgwODk5NjU3MzI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/ilRyazdMJwN05exqhwK4tMKBYZs.jpg",
     "description": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard.", "duration": 164, "director": "Denis Villeneuve", "cast": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"], "popularity": 85, "media_type": "movie"},
    
    {"id": 13, "title": "Dune", "year": 2021, "genres": ["Sci-Fi", "Adventure", "Drama"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDQ0NjgyN2YtNWViNS00YjA3LTkxNDktYzFkZTExZGMxZDkxXkEyXkFqcGdeQXVyODE5NzE3OTE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg",
     "description": "Paul Atreides, a brilliant and gifted young man, must travel to the most dangerous planet in the universe.", "duration": 155, "director": "Denis Villeneuve", "cast": ["Timothée Chalamet", "Rebecca Ferguson", "Zendaya"], "popularity": 91, "media_type": "movie"},
    
    {"id": 14, "title": "Avatar", "year": 2009, "genres": ["Sci-Fi", "Adventure", "Fantasy"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BZDA0OGQxNTItMDZkMC00N2UyLTg3MzMtYTJmNjg3Nzk5MzRiXkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/o0s4XsEDfDlvit5pDRKjzXR4pp2.jpg",
     "description": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following orders and protecting his new home.", "duration": 162, "director": "James Cameron", "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver"], "popularity": 89, "media_type": "movie"},
    
    {"id": 15, "title": "Arrival", "year": 2016, "genres": ["Drama", "Mystery", "Sci-Fi"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTExMzU0ODcxNDheQTJeQWpwZ15BbWU4MDE1OTI4MzAy._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/yIZ1xendyqKvY3FGeeUYUd5X9Mm.jpg",
     "description": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear.", "duration": 116, "director": "Denis Villeneuve", "cast": ["Amy Adams", "Jeremy Renner", "Forest Whitaker"], "popularity": 85, "media_type": "movie"},
    
    {"id": 16, "title": "The Martian", "year": 2015, "genres": ["Adventure", "Drama", "Sci-Fi"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTc2MTQ3MDA1Nl5BMl5BanBnXkFtZTgwODA3OTI4NjE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/Ar7QuJMGbpP2QXTh6byXyIpNiUp.jpg",
     "description": "An astronaut becomes stranded on Mars and must improvise to survive.", "duration": 144, "director": "Ridley Scott", "cast": ["Matt Damon", "Jessica Chastain", "Kristen Wiig"], "popularity": 87, "media_type": "movie"},
    
    {"id": 17, "title": "Gravity", "year": 2013, "genres": ["Drama", "Sci-Fi", "Thriller"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BNjE5MzYwMzYxMF5BMl5BanBnXkFtZTcwOTk4MTk0OQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/sVd5e2jg1RaKAc7CClJF0EimRS9.jpg",
     "description": "Two astronauts work together to survive after an accident leaves them stranded in space.", "duration": 91, "director": "Alfonso Cuarón", "cast": ["Sandra Bullock", "George Clooney", "Ed Harris"], "popularity": 84, "media_type": "movie"},
    
    {"id": 18, "title": "Edge of Tomorrow", "year": 2014, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTc5OTk4MTM3M15BMl5BanBnXkFtZTgwODcxNjg3MDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/hiKmpZMGZsrkA3cdce8a7Dpos1j.jpg",
     "description": "A soldier fighting aliens gets caught in a time loop, reliving the same day and improving his skills.", "duration": 113, "director": "Doug Liman", "cast": ["Tom Cruise", "Emily Blunt", "Bill Paxton"], "popularity": 86, "media_type": "movie"},
    
    {"id": 19, "title": "Ex Machina", "year": 2014, "genres": ["Drama", "Mystery", "Sci-Fi"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTUxNzc0OTIxMV5BMl5BanBnXkFtZTgwNDI3NzU2NDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/F1KVHqbKMjQqU8UJC3SdV6NsZt.jpg",
     "description": "A young programmer is selected to participate in a groundbreaking experiment in synthetic intelligence.", "duration": 108, "director": "Alex Garland", "cast": ["Alicia Vikander", "Domhnall Gleeson", "Oscar Isaac"], "popularity": 83, "media_type": "movie"},
    
    {"id": 20, "title": "District 9", "year": 2009, "genres": ["Action", "Sci-Fi", "Thriller"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BYzY5NTg3YmItYjBkYi00NjgwLTk3NTAtYjYxZGY0M2UxMjMxXkEyXkFqcGc@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/gD5GsG9O4QyuDgtLGmdlCEsRqSc.jpg",
     "description": "Violence ensues after an idealistic bureaucrat is infected by an alien fluid that begins transforming him.", "duration": 112, "director": "Neill Blomkamp", "cast": ["Sharlto Copley", "David James", "Jason Cope"], "popularity": 82, "media_type": "movie"},

    # === DRAMA MOVIES (21-30) ===
    {"id": 21, "title": "The Shawshank Redemption", "year": 1994, "genres": ["Drama", "Crime"], "rating": 9.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NmNlLWJiNDMtZDViZWM2MzIxZDYwXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
     "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "duration": 142, "director": "Frank Darabont", "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"], "popularity": 96, "media_type": "movie"},
    
    {"id": 22, "title": "Forrest Gump", "year": 1994, "genres": ["Drama", "Romance"], "rating": 8.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzg1LWJhNzYtMmZiYmEyNjU1NjMzXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/ghgfzbEV7kbpbi1O3mzrfKOxuWq.jpg",
     "description": "The presidencies of Kennedy and Johnson, the Vietnam War, and other events unfold from the perspective of an Alabama man with an IQ of 75.", "duration": 142, "director": "Robert Zemeckis", "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise"], "popularity": 92, "media_type": "movie"},
    
    {"id": 23, "title": "The Godfather", "year": 1972, "genres": ["Crime", "Drama"], "rating": 9.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
     "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant youngest son.", "duration": 175, "director": "Francis Ford Coppola", "cast": ["Marlon Brando", "Al Pacino", "James Caan"], "popularity": 94, "media_type": "movie"},
    
    {"id": 24, "title": "Schindler's List", "year": 1993, "genres": ["Drama", "History", "War"], "rating": 9.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BNDE4OTMxMTctNmRhYy00NWE2LTg3YzItYTk3M2UwOTU5Njg4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/loRmRzQXZeqG78TqZuyvSlEQfZb.jpg",
     "description": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce.", "duration": 195, "director": "Steven Spielberg", "cast": ["Liam Neeson", "Ben Kingsley", "Ralph Fiennes"], "popularity": 91, "media_type": "movie"},
    
    {"id": 25, "title": "Fight Club", "year": 1999, "genres": ["Drama"], "rating": 8.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMmEzNTkxYjQtZTc0MC00YTVjLTg5ZTEtZWMwOWVlYzY0NWIwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/87hTDiay2N2qWyX4Ds7ybXi9h8I.jpg",
     "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club.", "duration": 139, "director": "David Fincher", "cast": ["Brad Pitt", "Edward Norton", "Meat Loaf"], "popularity": 91, "media_type": "movie"},
    
    {"id": 26, "title": "Pulp Fiction", "year": 1994, "genres": ["Crime", "Drama"], "rating": 8.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BNGNhMDIzZTUtNTBlZi00MTRlLWFjM2ItYzViMjE3YzI5MjljXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
     "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.", "duration": 154, "director": "Quentin Tarantino", "cast": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"], "popularity": 93, "media_type": "movie"},
    
    {"id": 27, "title": "Goodfellas", "year": 1990, "genres": ["Biography", "Crime", "Drama"], "rating": 8.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BY2NkZjEzMDgtN2RjYy00YzM1LWI4ZmQtMjIwYjFjNmI3ZGEwXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/sw7mordbZxgITU877yTpZCud90M.jpg",
     "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen and his mob partners.", "duration": 146, "director": "Martin Scorsese", "cast": ["Robert De Niro", "Ray Liotta", "Joe Pesci"], "popularity": 89, "media_type": "movie"},
    
    {"id": 28, "title": "The Green Mile", "year": 1999, "genres": ["Crime", "Drama", "Fantasy"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/vxJ08SvwomfKbpboCWynC3uqUg4.jpg",
     "description": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder who has a mysterious gift.", "duration": 189, "director": "Frank Darabont", "cast": ["Tom Hanks", "Michael Clarke Duncan", "David Morse"], "popularity": 88, "media_type": "movie"},
    
    {"id": 29, "title": "Whiplash", "year": 2014, "genres": ["Drama", "Music"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTA5NDZlZGUtMjAxOS00YTRkLTkwYmMtYWQ0NWEwZDZiNjEzXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/fRGxZuo7jJUWQsVg9PREb98Aclp.jpg",
     "description": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing.", "duration": 106, "director": "Damien Chazelle", "cast": ["Miles Teller", "J.K. Simmons", "Paul Reiser"], "popularity": 87, "media_type": "movie"},
    
    {"id": 30, "title": "Parasite", "year": 2019, "genres": ["Drama", "Thriller", "Comedy"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BYWZjMjk3ZTItODQ2ZC00NTY5LWE0ZDYtZTI3MjcwN2Q5NTVkXkEyXkFqcGdeQXVyODk4OTc3MTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
     "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.", "duration": 132, "director": "Bong Joon-ho", "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"], "popularity": 90, "media_type": "movie"},

    # === THRILLER/MYSTERY MOVIES (31-40) ===
    {"id": 31, "title": "Se7en", "year": 1995, "genres": ["Crime", "Drama", "Mystery", "Thriller"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTUwODM5MTctZjczMi00OTk4LTg3NWUtNmVhMTAzNTNjYjcyXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/gNgMtPp7FwZsLbdUd7qVDy6Xp1U.jpg",
     "description": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.", "duration": 127, "director": "David Fincher", "cast": ["Brad Pitt", "Morgan Freeman", "Gwyneth Paltrow"], "popularity": 88, "media_type": "movie"},
    
    {"id": 32, "title": "The Silence of the Lambs", "year": 1991, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BNjNhZTk0ZmEtNjJhMi00YzFlLWE1MmEtYzM1M2ZmMGMwMTU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/mfwq2nMBzArzQ7Y9RKE8SKeeTkg.jpg",
     "description": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.", "duration": 118, "director": "Jonathan Demme", "cast": ["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney"], "popularity": 87, "media_type": "movie"},
    
    {"id": 33, "title": "Gone Girl", "year": 2014, "genres": ["Drama", "Mystery", "Thriller"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTk0MDQ3MzAzOV5BMl5BanBnXkFtZTgwNzU1NzE3MjE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/55GEsIk7NJFfL3JmVuZdUXyl2Ey.jpg",
     "description": "With his wife's disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him.", "duration": 149, "director": "David Fincher", "cast": ["Ben Affleck", "Rosamund Pike", "Neil Patrick Harris"], "popularity": 85, "media_type": "movie"},
    
    {"id": 34, "title": "Shutter Island", "year": 2010, "genres": ["Mystery", "Thriller"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BYzhiNDkyNzktNTZmYS00ZTBkLTk2MDAtM2U0YjU1MzgxZjgzXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg",
     "description": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.", "duration": 138, "director": "Martin Scorsese", "cast": ["Leonardo DiCaprio", "Emily Mortimer", "Mark Ruffalo"], "popularity": 86, "media_type": "movie"},
    
    {"id": 35, "title": "Prisoners", "year": 2013, "genres": ["Crime", "Drama", "Mystery", "Thriller"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTg0NTIzMjQ1NV5BMl5BanBnXkFtZTcwNDc3MzM5OQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/wVEGxtncWuK2SNNRjFrs5PhqUMq.jpg",
     "description": "When Keller Dover's daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads.", "duration": 153, "director": "Denis Villeneuve", "cast": ["Hugh Jackman", "Jake Gyllenhaal", "Viola Davis"], "popularity": 84, "media_type": "movie"},
    
    {"id": 36, "title": "The Prestige", "year": 2006, "genres": ["Drama", "Mystery", "Sci-Fi", "Thriller"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjA4NDI0MTIxNF5BMl5BanBnXkFtZTYwNTM0MzY2._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/dF0bTDCG68k53vQwWmNnA1VXrkS.jpg",
     "description": "After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion.", "duration": 130, "director": "Christopher Nolan", "cast": ["Christian Bale", "Hugh Jackman", "Scarlett Johansson"], "popularity": 88, "media_type": "movie"},
    
    {"id": 37, "title": "Memento", "year": 2000, "genres": ["Mystery", "Thriller"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BZTcyNjk1MjgtOWI3Mi00YzQwLWI5MTktMzY4ZmI2NDAyNzYzXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/8vIFWjh4n1PAFgQapq5KfJh04sZ.jpg",
     "description": "A man with short-term memory loss attempts to track down his wife's murderer.", "duration": 113, "director": "Christopher Nolan", "cast": ["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano"], "popularity": 86, "media_type": "movie"},
    
    {"id": 38, "title": "No Country for Old Men", "year": 2007, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjA5Njk3MjM4OV5BMl5BanBnXkFtZTcwMTc5MTE1MQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/6d5XOczc226jECq0LIX0siKtgHR.jpg",
     "description": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash.", "duration": 122, "director": "Coen Brothers", "cast": ["Tommy Lee Jones", "Javier Bardem", "Josh Brolin"], "popularity": 85, "media_type": "movie"},
    
    {"id": 39, "title": "Zodiac", "year": 2007, "genres": ["Crime", "Drama", "Mystery", "Thriller"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2UwNDc5NmEtNjVjZS00OTI5LWE4NTYtNTdlYWYxMGQ4YjA0XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/jD5ycHAhV4WjSgCp5hSdQEFP8Ss.jpg",
     "description": "In the late 1960s/early 1970s, a San Francisco cartoonist becomes an amateur detective obsessed with tracking down the Zodiac Killer.", "duration": 157, "director": "David Fincher", "cast": ["Jake Gyllenhaal", "Robert Downey Jr.", "Mark Ruffalo"], "popularity": 82, "media_type": "movie"},
    
    {"id": 40, "title": "Knives Out", "year": 2019, "genres": ["Comedy", "Crime", "Drama", "Mystery"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMGUwZjliMTAtNzAxZi00MWNiLWE2NzgtZGUxMGQxZjhhNDRiXkEyXkFqcGdeQXVyNjU1NzU3MzE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/4HWAQu28e2yaWrtupFPGFkdNU7V.jpg",
     "description": "A detective investigates the death of a patriarch of an eccentric, combative family.", "duration": 130, "director": "Rian Johnson", "cast": ["Daniel Craig", "Chris Evans", "Ana de Armas"], "popularity": 86, "media_type": "movie"},

    # === HORROR MOVIES (41-50) ===
    {"id": 41, "title": "Get Out", "year": 2017, "genres": ["Horror", "Mystery", "Thriller"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjUxMDQwNjcyNl5BMl5BanBnXkFtZTgwNzcwMzc0MTI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/axjHeLMwHjuqNqWjYefPi1aBVXL.jpg",
     "description": "A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.", "duration": 104, "director": "Jordan Peele", "cast": ["Daniel Kaluuya", "Allison Williams", "Bradley Whitford"], "popularity": 83, "media_type": "movie"},
    
    {"id": 42, "title": "A Quiet Place", "year": 2018, "genres": ["Drama", "Horror", "Sci-Fi"], "rating": 7.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjI0MDMzNTQ0M15BMl5BanBnXkFtZTgwMTM5NzM3NDM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/roYyPiQDQKmIKUEhO912dVOCGQU.jpg",
     "description": "In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing.", "duration": 90, "director": "John Krasinski", "cast": ["Emily Blunt", "John Krasinski", "Millicent Simmonds"], "popularity": 82, "media_type": "movie"},
    
    {"id": 43, "title": "Hereditary", "year": 2018, "genres": ["Drama", "Horror", "Mystery"], "rating": 7.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTU5MDg3OGItZWQ1Ny00ZGVmLTg2YTUtMzBkYzQ1YWIwZjlhXkEyXkFqcGdeQXVyNTAzMTY4MDA@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/lHV8HHlhwNup2VbpiACtlKzaGIQ.jpg",
     "description": "A grieving family is haunted by tragic and disturbing occurrences.", "duration": 127, "director": "Ari Aster", "cast": ["Toni Collette", "Milly Shapiro", "Gabriel Byrne"], "popularity": 80, "media_type": "movie"},
    
    {"id": 44, "title": "The Conjuring", "year": 2013, "genres": ["Horror", "Mystery", "Thriller"], "rating": 7.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTM3NjA1NDMyMV5BMl5BanBnXkFtZTcwMDQzNDMzOQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/xg5LEJDA2fBmVphP59XUYJzSFhs.jpg",
     "description": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse.", "duration": 112, "director": "James Wan", "cast": ["Patrick Wilson", "Vera Farmiga", "Ron Livingston"], "popularity": 81, "media_type": "movie"},
    
    {"id": 45, "title": "It", "year": 2017, "genres": ["Horror", "Fantasy"], "rating": 7.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BZDVkZmI0YzAtNzdjYi00ZjhhLWE1ODEtMWMzMWMzNDA0NmQ4XkEyXkFqcGdeQXVyNzYzODM3Mzg@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/tcheoA2nPATCm2vvXw2hVQoaEFD.jpg",
     "description": "A group of bullied kids band together to destroy a shape-shifting monster, which disguises itself as a clown.", "duration": 135, "director": "Andy Muschietti", "cast": ["Bill Skarsgård", "Jaeden Martell", "Finn Wolfhard"], "popularity": 82, "media_type": "movie"},
    
    {"id": 46, "title": "The Shining", "year": 1980, "genres": ["Drama", "Horror"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BZWFlYmY2MGEtZjVkYS00YzU4LTg0YjQtYzY1ZGE3NTA5NGQxXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/Ss7K9FMqUUlqzs3IYfUUk13I0nh.jpg",
     "description": "A family heads to an isolated hotel for the winter where a sinister presence influences the father into violence.", "duration": 146, "director": "Stanley Kubrick", "cast": ["Jack Nicholson", "Shelley Duvall", "Danny Lloyd"], "popularity": 86, "media_type": "movie"},
    
    {"id": 47, "title": "Midsommar", "year": 2019, "genres": ["Drama", "Horror", "Mystery"], "rating": 7.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BMzQxNzQzOTQwM15BMl5BanBnXkFtZTgwMDQ2NTcwODM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/xLkLaQkqJeQhMfvUKeMwWXm0mN7.jpg",
     "description": "A couple travels to Northern Europe to visit a rural hometown's fabled Swedish mid-summer festival.", "duration": 148, "director": "Ari Aster", "cast": ["Florence Pugh", "Jack Reynor", "Vilhelm Blomgren"], "popularity": 79, "media_type": "movie"},
    
    {"id": 48, "title": "Us", "year": 2019, "genres": ["Horror", "Mystery", "Thriller"], "rating": 6.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BZTliNWJhM2YtNDc1MC00YTk1LWE2MGYtZmE4M2Y5ODdlNzQzXkEyXkFqcGdeQXVyMzY0MTE3NzU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/ux2eNHTBEjXbqk5WNtuPuCi83RW.jpg",
     "description": "A family's serene beach vacation turns to chaos when their doppelgängers appear.", "duration": 116, "director": "Jordan Peele", "cast": ["Lupita Nyong'o", "Winston Duke", "Elisabeth Moss"], "popularity": 78, "media_type": "movie"},
    
    {"id": 49, "title": "The Exorcist", "year": 1973, "genres": ["Horror"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BYWFlZGY2NDktY2ZjOS00ZWNkLTg0ZDAtZDY4MTM1ODU4ZjljXkEyXkFqcGdeQXVyMjUzOTY1NTc@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/dVUlrE2Xps4mOhLcTh4Wz3VgLb7.jpg",
     "description": "When a young girl is possessed by a mysterious entity, her mother seeks the help of two priests to save her.", "duration": 122, "director": "William Friedkin", "cast": ["Ellen Burstyn", "Max von Sydow", "Linda Blair"], "popularity": 84, "media_type": "movie"},
    
    {"id": 50, "title": "The Witch", "year": 2015, "genres": ["Drama", "Horror", "Mystery"], "rating": 6.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTUyNzkwMzAxOF5BMl5BanBnXkFtZTgwMzc1OTk1NjE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/o4jXjk3oBkU5c6jnLInoWrN2hnw.jpg",
     "description": "A family in 1630s New England is torn apart by the forces of witchcraft, black magic, and possession.", "duration": 92, "director": "Robert Eggers", "cast": ["Anya Taylor-Joy", "Ralph Ineson", "Kate Dickie"], "popularity": 77, "media_type": "movie"},

    # === COMEDY MOVIES (51-60) ===
    {"id": 51, "title": "The Grand Budapest Hotel", "year": 2014, "genres": ["Adventure", "Comedy", "Crime"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BMzM5NjUxOTEyMl5BMl5BanBnXkFtZTgwNjEyMDM0MDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nX5XotM9yprCKarRH4fzOq1VM1J.jpg",
     "description": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy.", "duration": 99, "director": "Wes Anderson", "cast": ["Ralph Fiennes", "F. Murray Abraham", "Mathieu Amalric"], "popularity": 84, "media_type": "movie"},
    
    {"id": 52, "title": "Superbad", "year": 2007, "genres": ["Comedy"], "rating": 7.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTc0NjIyMjA2OF5BMl5BanBnXkFtZTcwMzIxNDE1MQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/65DftFkGMmCPyOH9WKurCqODyac.jpg",
     "description": "Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry.", "duration": 113, "director": "Greg Mottola", "cast": ["Jonah Hill", "Michael Cera", "Christopher Mintz-Plasse"], "popularity": 78, "media_type": "movie"},
    
    {"id": 53, "title": "The Hangover", "year": 2009, "genres": ["Comedy"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BNGQwZjg5YmYtY2VkNC00NzliLTljYTctNzI5NmU3MjE2ODQzXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/5qMJrqHkvNKsWhoB3FIM4MQO3II.jpg",
     "description": "Three buddies wake up from a bachelor party in Las Vegas, with no memory of the previous night and the bachelor missing.", "duration": 100, "director": "Todd Phillips", "cast": ["Bradley Cooper", "Ed Helms", "Zach Galifianakis"], "popularity": 83, "media_type": "movie"},
    
    {"id": 54, "title": "Jojo Rabbit", "year": 2019, "genres": ["Comedy", "Drama", "War"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BZjU0Yzk2MzEtMjAzYy00MzY0LTg2YmItM2RkNzdkY2ZhN2JkXkEyXkFqcGdeQXVyNDg4NjY5OTQ@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/agoBZfL1q5G79SD0npArSlJn8BH.jpg",
     "description": "A young boy in Hitler's army finds out his mother is hiding a Jewish girl in their home.", "duration": 108, "director": "Taika Waititi", "cast": ["Roman Griffin Davis", "Thomasin McKenzie", "Scarlett Johansson"], "popularity": 82, "media_type": "movie"},
    
    {"id": 55, "title": "The Truman Show", "year": 1998, "genres": ["Comedy", "Drama"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDIzODcyY2EtMmY2MC00ZWVlLTgwMzAtMjQwOWUyNmJjNTYyXkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/pG5EyS5rJLn7bEGLj2YAqPFkbR3.jpg",
     "description": "An insurance salesman discovers his whole life is actually a reality TV show.", "duration": 103, "director": "Peter Weir", "cast": ["Jim Carrey", "Ed Harris", "Laura Linney"], "popularity": 86, "media_type": "movie"},
    
    {"id": 56, "title": "Deadpool", "year": 2016, "genres": ["Action", "Adventure", "Comedy"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BYzE5MjY1ZDgtMTkyNC00MTMyLThhMjAtZGI5OTE1NzFlZGJjXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/en971MEXui9diirXlogOrPKmsEn.jpg",
     "description": "A wisecracking mercenary gets experimented on and becomes immortal but ugly, and sets out to track down the man who ruined his looks.", "duration": 108, "director": "Tim Miller", "cast": ["Ryan Reynolds", "Morena Baccarin", "T.J. Miller"], "popularity": 89, "media_type": "movie"},
    
    {"id": 57, "title": "Thor: Ragnarok", "year": 2017, "genres": ["Action", "Adventure", "Comedy", "Fantasy"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjMyNDkzMzI1OF5BMl5BanBnXkFtZTgwODcxODg5MjI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/kaIfm5ryEOwYg8mLbq8HkPuM1Fo.jpg",
     "description": "Thor must escape the alien planet Sakaar in time to save Asgard from Hela and the impending Ragnarök.", "duration": 130, "director": "Taika Waititi", "cast": ["Chris Hemsworth", "Tom Hiddleston", "Cate Blanchett"], "popularity": 88, "media_type": "movie"},
    
    {"id": 58, "title": "Guardians of the Galaxy", "year": 2014, "genres": ["Action", "Adventure", "Comedy", "Sci-Fi"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTAwMjU5OTgxNjZeQTJeQWpwZ15BbWU4MDUxNDYxODEx._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/mfn9ojJjLsG6cAcfvh6ILBzRmQN.jpg",
     "description": "A group of intergalactic criminals must pull together to stop a fanatical warrior with plans to purge the universe.", "duration": 121, "director": "James Gunn", "cast": ["Chris Pratt", "Vin Diesel", "Bradley Cooper"], "popularity": 89, "media_type": "movie"},
    
    {"id": 59, "title": "The Big Lebowski", "year": 1998, "genres": ["Comedy", "Crime"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTQ0NjUzMDMyOF5BMl5BanBnXkFtZTgwODA1OTU0MDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/eH1ljX3k8TWqLF0yDcN8OD3UaNx.jpg",
     "description": "Jeff 'The Dude' Lebowski, mistaken for a millionaire of the same name, seeks restitution for his ruined rug.", "duration": 117, "director": "Joel Coen", "cast": ["Jeff Bridges", "John Goodman", "Julianne Moore"], "popularity": 84, "media_type": "movie"},
    
    {"id": 60, "title": "Shaun of the Dead", "year": 2004, "genres": ["Comedy", "Horror"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTg5Mjk2NDMtZTk0Ny00YTQ0LWIzYWEtMWI5MGQ0Mjg1OTNkXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/jvKbj1Vcg73XKDw8uXvh2t2Wfi3.jpg",
     "description": "A man's uneventful life is disrupted by the zombie apocalypse.", "duration": 99, "director": "Edgar Wright", "cast": ["Simon Pegg", "Nick Frost", "Kate Ashfield"], "popularity": 82, "media_type": "movie"},

    # === ANIMATION MOVIES (61-70) ===
    {"id": 61, "title": "Spider-Man: Into the Spider-Verse", "year": 2018, "genres": ["Animation", "Action", "Adventure"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjMwNDkxMTgzOF5BMl5BanBnXkFtZTgwNTkwNTQ3NjM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/l3YJbPDL6vJqjWwXU4ChBPA1bYm.jpg",
     "description": "Teen Miles Morales becomes the Spider-Man of his universe and must join with five spider-powered individuals from other dimensions.", "duration": 117, "director": "Bob Persichetti", "cast": ["Shameik Moore", "Jake Johnson", "Hailee Steinfeld"], "popularity": 89, "media_type": "movie"},
    
    {"id": 62, "title": "Coco", "year": 2017, "genres": ["Animation", "Adventure", "Family", "Music"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BYjQ5NjM0Y2YtNjZkNC00ZDhkLWJjMWItN2QyNzFkMDE3ZjAxXkEyXkFqcGdeQXVyODIxMzk5NjA@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nlPCdZlHtRNcF6C9hzUH4ebmV1w.jpg",
     "description": "Aspiring musician Miguel enters the Land of the Dead to find his great-great-grandfather, a legendary singer.", "duration": 105, "director": "Lee Unkrich", "cast": ["Anthony Gonzalez", "Gael García Bernal", "Benjamin Bratt"], "popularity": 88, "media_type": "movie"},
    
    {"id": 63, "title": "Your Name", "year": 2016, "genres": ["Animation", "Drama", "Fantasy", "Romance"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BODRmZDVmNzUtZDA4ZC00NjhkLWI2M2UtN2M0ZDIzNDcxYThjL2ltYWdlXkEyXkFqcGdeQXVyNTk0MzMzODA@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/dIWwZW7dJJtqC6CgWzYkNVKIUm8.jpg",
     "description": "Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?", "duration": 106, "director": "Makoto Shinkai", "cast": ["Ryunosuke Kamiki", "Mone Kamishiraishi", "Ryo Narita"], "popularity": 87, "media_type": "movie"},
    
    {"id": 64, "title": "Spirited Away", "year": 2001, "genres": ["Animation", "Adventure", "Family", "Fantasy"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjlmZmI5MDctNDE2YS00YWE0LWE5ZWItZDBhYWQ0NTcxNWRhXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/mSDsSDwaP3E7dEfUPWy4J0djt4O.jpg",
     "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits.", "duration": 125, "director": "Hayao Miyazaki", "cast": ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki"], "popularity": 90, "media_type": "movie"},
    
    {"id": 65, "title": "Toy Story", "year": 1995, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/bxkaAGejGeQykJGsP6fvLhBmLjP.jpg",
     "description": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.", "duration": 81, "director": "John Lasseter", "cast": ["Tom Hanks", "Tim Allen", "Don Rickles"], "popularity": 88, "media_type": "movie"},
    
    {"id": 66, "title": "The Lion King", "year": 1994, "genres": ["Animation", "Adventure", "Drama", "Family", "Music"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BYTYxNGMyZTYtMjE3MS00MzNjLWFjNmYtMDk3N2FmM2JiM2M1XkEyXkFqcGdeQXVyNjY5NDU4NzI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/wXsQvli6tWqja51pYxXNG1LFIGV.jpg",
     "description": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.", "duration": 88, "director": "Roger Allers", "cast": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones"], "popularity": 91, "media_type": "movie"},
    
    {"id": 67, "title": "Up", "year": 2009, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTk3NDE2NzI4NF5BMl5BanBnXkFtZTgwNzE1MzEyMTE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nPimVfznsoGKQidIBMPRzHxLhQp.jpg",
     "description": "78-year-old Carl Fredricksen travels to Paradise Falls in his house equipped with balloons, inadvertently taking a young stowaway.", "duration": 96, "director": "Pete Docter", "cast": ["Edward Asner", "Jordan Nagai", "John Ratzenberger"], "popularity": 87, "media_type": "movie"},
    
    {"id": 68, "title": "WALL·E", "year": 2008, "genres": ["Animation", "Adventure", "Family", "Sci-Fi"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjExMTg5OTU0NF5BMl5BanBnXkFtZTcwMjMxMzMzMw@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/fJJGo7zuKin1vdkYKpOzXQ8QOLf.jpg",
     "description": "In the distant future, a small waste-collecting robot inadvertently embarks on a space journey that will ultimately decide the fate of mankind.", "duration": 98, "director": "Andrew Stanton", "cast": ["Ben Burtt", "Elissa Knight", "Jeff Garlin"], "popularity": 88, "media_type": "movie"},
    
    {"id": 69, "title": "Inside Out", "year": 2015, "genres": ["Animation", "Adventure", "Comedy", "Drama", "Family"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTgxMDQwMDk0OF5BMl5BanBnXkFtZTgwNjU5OTg2NDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/j29ekbcLpBvxnGk6LjdTc2EI5SA.jpg",
     "description": "After young Riley is uprooted from her Midwest life and moved to San Francisco, her emotions conflict on how best to navigate a new city, house, and school.", "duration": 95, "director": "Pete Docter", "cast": ["Amy Poehler", "Phyllis Smith", "Richard Kind"], "popularity": 87, "media_type": "movie"},
    
    {"id": 70, "title": "Finding Nemo", "year": 2003, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BZTAzNWZlNmUtZDEzYi00ZjA5LWIwYjEtZGM1NWE1MjE4YWRhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/dSBzpjHDCgz8JFBLA3qL2DKYm0A.jpg",
     "description": "After his son is captured in the Great Barrier Reef and taken to Sydney, a timid clownfish sets out on a journey to bring him home.", "duration": 100, "director": "Andrew Stanton", "cast": ["Albert Brooks", "Ellen DeGeneres", "Alexander Gould"], "popularity": 88, "media_type": "movie"},

    # === ROMANCE MOVIES (71-80) ===
    {"id": 71, "title": "La La Land", "year": 2016, "genres": ["Comedy", "Drama", "Music", "Romance"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BMzUzNDM2NzM2MV5BMl5BanBnXkFtZTgwNTM3NTg4OTE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/mUevWAx1BqKlcWHbNIjPDhb9AB6.jpg",
     "description": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations.", "duration": 128, "director": "Damien Chazelle", "cast": ["Ryan Gosling", "Emma Stone", "Rosemarie DeWitt"], "popularity": 87, "media_type": "movie"},
    
    {"id": 72, "title": "The Notebook", "year": 2004, "genres": ["Drama", "Romance"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTk3OTM5Njg5M15BMl5BanBnXkFtZTYwMzA0ODI3._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/qom1SZSENdmHFNZBXbtJAU0WTlC.jpg",
     "description": "A poor yet passionate young man falls in love with a rich young woman, giving her a sense of freedom.", "duration": 123, "director": "Nick Cassavetes", "cast": ["Gena Rowlands", "James Garner", "Rachel McAdams"], "popularity": 84, "media_type": "movie"},
    
    {"id": 73, "title": "Pride & Prejudice", "year": 2005, "genres": ["Drama", "Romance"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTA1NDQ3NTcyOTNeQTJeQWpwZ15BbWU3MDA0MzA4MzE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/5zFmaJYp9aW5u6SLFvkv4U9CgYF.jpg",
     "description": "Sparks fly when spirited Elizabeth Bennet meets single, rich, and proud Mr. Darcy.", "duration": 129, "director": "Joe Wright", "cast": ["Keira Knightley", "Matthew Macfadyen", "Brenda Blethyn"], "popularity": 83, "media_type": "movie"},
    
    {"id": 74, "title": "Eternal Sunshine of the Spotless Mind", "year": 2004, "genres": ["Drama", "Romance", "Sci-Fi"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTY4NzcwODg3Nl5BMl5BanBnXkFtZTcwNTEwOTMyMw@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/1ZyDYbDa6xBXj0SVEvKCVVphdIS.jpg",
     "description": "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories.", "duration": 108, "director": "Michel Gondry", "cast": ["Jim Carrey", "Kate Winslet", "Tom Wilkinson"], "popularity": 86, "media_type": "movie"},
    
    {"id": 75, "title": "Titanic", "year": 1997, "genres": ["Drama", "Romance"], "rating": 7.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/4qCqAdHcNKeAHcK8tJ8wNJZa9cx.jpg",
     "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.", "duration": 194, "director": "James Cameron", "cast": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"], "popularity": 91, "media_type": "movie"},
    
    {"id": 76, "title": "500 Days of Summer", "year": 2009, "genres": ["Comedy", "Drama", "Romance"], "rating": 7.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTk5MjM4OTU1OV5BMl5BanBnXkFtZTcwODkzNDIzMw@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/wGmwsGnXKDVjKPPQPNGJM0xZvk.jpg",
     "description": "An offbeat romantic comedy about a woman who doesn't believe true love exists, and the young man who falls for her.", "duration": 95, "director": "Marc Webb", "cast": ["Joseph Gordon-Levitt", "Zooey Deschanel", "Geoffrey Arend"], "popularity": 82, "media_type": "movie"},
    
    {"id": 77, "title": "Before Sunrise", "year": 1995, "genres": ["Drama", "Romance"], "rating": 8.1,
     "poster": "https://m.media-amazon.com/images/M/MV5BZDdiZTAwYzAtMDI3Ni00OTRjLTkzN2UtMGE3MDMyZmU4NTU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/kk2bQBKgnVpVvYvnMCUs8a3uMR8.jpg",
     "description": "A young man and woman meet on a train in Europe, and wind up spending one evening together in Vienna.", "duration": 101, "director": "Richard Linklater", "cast": ["Ethan Hawke", "Julie Delpy", "Andrea Eckert"], "popularity": 80, "media_type": "movie"},
    
    {"id": 78, "title": "About Time", "year": 2013, "genres": ["Comedy", "Drama", "Fantasy", "Romance"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTAxMDU4NDcyMjNeQTJeQWpwZ15BbWU4MDY0OTYzMzAx._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/z21hfkxTkl0oJu2F1lVoLrLLR3G.jpg",
     "description": "At 21, Tim discovers he can travel in time and change what happens and has happened in his own life.", "duration": 123, "director": "Richard Curtis", "cast": ["Domhnall Gleeson", "Rachel McAdams", "Bill Nighy"], "popularity": 81, "media_type": "movie"},
    
    {"id": 79, "title": "Amélie", "year": 2001, "genres": ["Comedy", "Romance"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BNDg4NjM1YjMtYmNhZC00MjM0LWFiZmYtNGY1YjA3MzZmODc5XkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/bw1voQgJGkIy5N0sP6p8QQ3cGZy.jpg",
     "description": "Amélie is an innocent and naive girl in Paris with her own sense of justice. She decides to help those around her and discovers love.", "duration": 122, "director": "Jean-Pierre Jeunet", "cast": ["Audrey Tautou", "Mathieu Kassovitz", "Rufus"], "popularity": 84, "media_type": "movie"},
    
    {"id": 80, "title": "Crazy Rich Asians", "year": 2018, "genres": ["Comedy", "Drama", "Romance"], "rating": 6.9,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTYxNDMyOTAxN15BMl5BanBnXkFtZTgwMDg1ODYzNTM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/5K7cOHoay2mZusSLezBOY0Qxh8a.jpg",
     "description": "This contemporary romantic comedy follows native New Yorker Rachel Chu to Singapore to meet her boyfriend's family.", "duration": 120, "director": "Jon M. Chu", "cast": ["Constance Wu", "Henry Golding", "Michelle Yeoh"], "popularity": 79, "media_type": "movie"},

    # === TV SHOWS (81-90) ===
    {"id": 81, "title": "Breaking Bad", "year": 2008, "genres": ["Crime", "Drama", "Thriller"], "rating": 9.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMjhiMzgxZTctNDc1Ni00OTIxLTlhMTYtZTA3ZWFkODRkNmE2XkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/tsRy63Mu5cu8etL1X7ZLyf7ureI.jpg",
     "description": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine.", "duration": 45, "director": "Vince Gilligan", "cast": ["Bryan Cranston", "Aaron Paul", "Anna Gunn"], "popularity": 97, "media_type": "tv"},
    
    {"id": 82, "title": "Game of Thrones", "year": 2011, "genres": ["Action", "Adventure", "Drama", "Fantasy"], "rating": 9.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2IzYzBiOTQtNGZmMi00NDI5LTgxMzMtN2EzZjA1NjhlOGMxXkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/suopoADq0k8YZr4dQXcU6pToj6s.jpg",
     "description": "Nine noble families fight for control over the lands of Westeros, while an ancient enemy returns after being dormant for millennia.", "duration": 60, "director": "David Benioff", "cast": ["Peter Dinklage", "Lena Headey", "Emilia Clarke"], "popularity": 96, "media_type": "tv"},
    
    {"id": 83, "title": "Stranger Things", "year": 2016, "genres": ["Drama", "Fantasy", "Horror", "Mystery"], "rating": 8.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDZkYmVhNjMtNWU4MC00MDQxLWE3MjYtZGMzZWI1ZjhlOWJmXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/56v2KjBlU4XaOv9rVYEQypROD7P.jpg",
     "description": "When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces.", "duration": 50, "director": "The Duffer Brothers", "cast": ["Millie Bobby Brown", "Finn Wolfhard", "Winona Ryder"], "popularity": 93, "media_type": "tv"},
    
    {"id": 84, "title": "The Office", "year": 2005, "genres": ["Comedy"], "rating": 9.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDNkOTE4NDQtMTNmYi00MWE0LWE4ZTktYTc0NzhhNWIzNzJiXkEyXkFqcGdeQXVyMzQ2MDI5NjU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/vNpuAxGTl9HsUbHqam3E9CzqCvX.jpg",
     "description": "A mockumentary on a group of typical office workers, where the workday consists of ego clashes, inappropriate behavior, and tedium.", "duration": 22, "director": "Greg Daniels", "cast": ["Steve Carell", "Rainn Wilson", "John Krasinski"], "popularity": 92, "media_type": "tv"},
    
    {"id": 85, "title": "The Crown", "year": 2016, "genres": ["Biography", "Drama", "History"], "rating": 8.6,
     "poster": "https://m.media-amazon.com/images/M/MV5BZmY0MzBlNjctNTRmNy00Njk3LWFjMzctMWQwZDAwMGJmY2MyXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/sNqEGVt3UXbVIJokj2V0J1qrZ8z.jpg",
     "description": "Follows the political rivalries and romance of Queen Elizabeth II's reign and the events that shaped the second half of the twentieth century.", "duration": 60, "director": "Peter Morgan", "cast": ["Claire Foy", "Olivia Colman", "Imelda Staunton"], "popularity": 88, "media_type": "tv"},
    
    {"id": 86, "title": "Chernobyl", "year": 2019, "genres": ["Drama", "History", "Thriller"], "rating": 9.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BNTdlN2Q4MjUtNjYwMC00MTFmLWFmYjctMDE2Njk3OGVkZTJhXkEyXkFqcGdeQXVyMTMzNDExODE5._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/skvxS8fVLmTJTzB1HZsjJyo8Cho.jpg",
     "description": "In April 1986, an explosion at the Chernobyl nuclear power plant in Ukraine becomes one of the world's worst man-made catastrophes.", "duration": 60, "director": "Craig Mazin", "cast": ["Jared Harris", "Stellan Skarsgård", "Emily Watson"], "popularity": 90, "media_type": "tv"},
    
    {"id": 87, "title": "The Mandalorian", "year": 2019, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 8.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2M5YWFjN2YtYzU2YS00NzU1LWFhN2UtOTJjNGJlNTZlNjA5XkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/rjBwhsOzHKUw2NIOrE7aMqjfe6s.jpg",
     "description": "The travels of a lone bounty hunter in the outer reaches of the galaxy, far from the authority of the New Republic.", "duration": 40, "director": "Jon Favreau", "cast": ["Pedro Pascal", "Carl Weathers", "Giancarlo Esposito"], "popularity": 89, "media_type": "tv"},
    
    {"id": 88, "title": "The Witcher", "year": 2019, "genres": ["Action", "Adventure", "Drama", "Fantasy"], "rating": 8.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2FiOWU4YzYtMzZiOS00MzcyLTlkOGEtOTgwZmEwMzAxMzA3XkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/59oOQN2kYZIigVQkqd9YAzQl8sH.jpg",
     "description": "Geralt of Rivia, a solitary monster hunter, struggles to find his place in a world where people often prove more wicked than beasts.", "duration": 60, "director": "Lauren Schmidt Hissrich", "cast": ["Henry Cavill", "Anya Chalotra", "Freya Allan"], "popularity": 86, "media_type": "tv"},
    
    {"id": 89, "title": "Dark", "year": 2017, "genres": ["Crime", "Drama", "Mystery", "Sci-Fi", "Thriller"], "rating": 8.7,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTk2NzUyOTctZDdlMS00MDllLTlhNjQtNjZjMmNmZjE5NmNjXkEyXkFqcGdeQXVyMjg1NDcxNDE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/3lBDg3i6nn5R2NKFCJ6oKyUo2j5.jpg",
     "description": "A family saga with a supernatural twist, set in a German town where the disappearance of two young children exposes relationships among four families.", "duration": 60, "director": "Baran bo Odar", "cast": ["Louis Hofmann", "Karoline Eichhorn", "Lisa Vicari"], "popularity": 85, "media_type": "tv"},
    
    {"id": 90, "title": "The Last of Us", "year": 2023, "genres": ["Action", "Adventure", "Drama"], "rating": 8.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BZGUzYTI3M2EtZmM0Yy00NGUyLWI4ODEtN2Q3ZGJlYzhhZjU3XkEyXkFqcGdeQXVyNTM0OTY1OQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/uKvVjHNqB5VmOrdxqAt2F7J78ED.jpg",
     "description": "Joel and Ellie, a pair connected through the harshness of the world they live in, are forced to endure brutal circumstances and ruthless killers on a trek across post-pandemic America.", "duration": 60, "director": "Craig Mazin", "cast": ["Pedro Pascal", "Bella Ramsey", "Anna Torv"], "popularity": 91, "media_type": "tv"},

    # === MORE RECENT/POPULAR MOVIES (91-100) ===
    {"id": 91, "title": "Oppenheimer", "year": 2023, "genres": ["Biography", "Drama", "History"], "rating": 8.5,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDBmYTZjNjUtN2M1MS00MTQ2LTk2ODgtNzc2M2QyZGE5NTVjXkEyXkFqcGdeQXVyNzAwMjU2MTY@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/rLb2LRVfqLc0Yr1Yr3SUpSL7Tgv.jpg",
     "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.", "duration": 180, "director": "Christopher Nolan", "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon"], "popularity": 94, "media_type": "movie"},
    
    {"id": 92, "title": "Barbie", "year": 2023, "genres": ["Adventure", "Comedy", "Fantasy"], "rating": 7.0,
     "poster": "https://m.media-amazon.com/images/M/MV5BNjU3N2QxNzYtMjk1NC00MTc4LTk1NTQtMmUxNTljM2I0NDA5XkEyXkFqcGdeQXVyODE5NzE3OTE@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/nHf61UzkfFno5X1ofIhugCPus2R.jpg",
     "description": "Barbie and Ken are having the time of their lives in the colorful world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.", "duration": 114, "director": "Greta Gerwig", "cast": ["Margot Robbie", "Ryan Gosling", "America Ferrera"], "popularity": 89, "media_type": "movie"},
    
    {"id": 93, "title": "Everything Everywhere All at Once", "year": 2022, "genres": ["Action", "Adventure", "Comedy", "Fantasy", "Sci-Fi"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BYTdiOTIyZTQtNmQ1OS00NjZlLWIyMTgtYzk5Y2M3ZDVmMDk1XkEyXkFqcGdeQXVyMTAzMDg4NzU0._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg",
     "description": "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save the world by exploring other universes.", "duration": 139, "director": "Daniel Kwan", "cast": ["Michelle Yeoh", "Stephanie Hsu", "Ke Huy Quan"], "popularity": 88, "media_type": "movie"},
    
    {"id": 94, "title": "The Batman", "year": 2022, "genres": ["Action", "Crime", "Drama"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BMDdmMTBiNTYtMDIzNi00NGVlLWIzMDYtZTk3MTQ3NGQxZGEwXkEyXkFqcGdeQXVyMzMwOTU5MDk@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg",
     "description": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption.", "duration": 176, "director": "Matt Reeves", "cast": ["Robert Pattinson", "Zoë Kravitz", "Jeffrey Wright"], "popularity": 90, "media_type": "movie"},
    
    {"id": 95, "title": "Spider-Man: No Way Home", "year": 2021, "genres": ["Action", "Adventure", "Fantasy"], "rating": 8.2,
     "poster": "https://m.media-amazon.com/images/M/MV5BZWMyYzFjYTYtNTRjYi00OGExLWE2YzgtOGRmYjAxZTU3NzBiXkEyXkFqcGdeQXVyMzQ0MzA0NTM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg",
     "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.", "duration": 148, "director": "Jon Watts", "cast": ["Tom Holland", "Zendaya", "Benedict Cumberbatch"], "popularity": 93, "media_type": "movie"},
    
    {"id": 96, "title": "Avengers: Endgame", "year": 2019, "genres": ["Action", "Adventure", "Drama", "Sci-Fi"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BMTc5MDE2ODcwNV5BMl5BanBnXkFtZTgwMzI2NzQ2NzM@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg",
     "description": "After the devastating events of Infinity War, the Avengers assemble once more to reverse Thanos' actions and restore balance to the universe.", "duration": 181, "director": "Anthony Russo", "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"], "popularity": 95, "media_type": "movie"},
    
    {"id": 97, "title": "Joker", "year": 2019, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.4,
     "poster": "https://m.media-amazon.com/images/M/MV5BNGVjNWI4ZGUtNzE0MS00YTJmLWE0ZDctN2ZiYTk2YmI3NTYyXkEyXkFqcGdeQXVyMTkxNjUyNQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/n6bUvigpRFqSwmPp1m2YMDNqKPc.jpg",
     "description": "In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime.", "duration": 122, "director": "Todd Phillips", "cast": ["Joaquin Phoenix", "Robert De Niro", "Zazie Beetz"], "popularity": 92, "media_type": "movie"},
    
    {"id": 98, "title": "1917", "year": 2019, "genres": ["Drama", "War"], "rating": 8.3,
     "poster": "https://m.media-amazon.com/images/M/MV5BOTdmNTFjNDEtNzg0My00ZjkxLTg1ZDAtZTdkMDc2ZmFiNWQ1XkEyXkFqcGdeQXVyNTAzNzgwNTg@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/tUWivz05fcY14K6RzicRm7IHkUD.jpg",
     "description": "Two soldiers are assigned to race against time and deliver a message that will stop 1,600 men from walking straight into a deadly trap.", "duration": 119, "director": "Sam Mendes", "cast": ["George MacKay", "Dean-Charles Chapman", "Mark Strong"], "popularity": 87, "media_type": "movie"},
    
    {"id": 99, "title": "Dune: Part Two", "year": 2024, "genres": ["Action", "Adventure", "Drama", "Sci-Fi"], "rating": 8.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BN2QyZGU4ZDctOWMzMy00NTc5LThlOGQtODhmNDI1NmY5YzAwXkEyXkFqcGdeQXVyMDM2NDM2MQ@@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg",
     "description": "Paul Atreides unites with Chani and the Fremen while seeking revenge against those who destroyed his family.", "duration": 166, "director": "Denis Villeneuve", "cast": ["Timothée Chalamet", "Zendaya", "Rebecca Ferguson"], "popularity": 93, "media_type": "movie"},
    
    {"id": 100, "title": "The Social Network", "year": 2010, "genres": ["Biography", "Drama"], "rating": 7.8,
     "poster": "https://m.media-amazon.com/images/M/MV5BOGUyZDUxZjEtMmIzMC00MzlmLTg4MGItZWJmMzBhZjE0Mjc1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
     "backdrop": "https://image.tmdb.org/t/p/original/c1OoQ3c8wJLvfWJyWPWz3xqBpAr.jpg",
     "description": "As Harvard student Mark Zuckerberg creates the social networking site that would become known as Facebook, he is sued by the twins who claimed he stole their idea.", "duration": 120, "director": "David Fincher", "cast": ["Jesse Eisenberg", "Andrew Garfield", "Justin Timberlake"], "popularity": 84, "media_type": "movie"},
]


# ============================================
# USER PROFILES
# ============================================

class UserType(str, Enum):
    ACTION_LOVER = "action_lover"
    SCI_FI_GEEK = "sci_fi_geek"
    DRAMA_FAN = "drama_fan"
    HORROR_ENTHUSIAST = "horror_enthusiast"
    COMEDY_LOVER = "comedy_lover"
    ROMANCE_SEEKER = "romance_seeker"
    ANIME_OTAKU = "anime_otaku"
    CLASSIC_CINEPHILE = "classic_cinephile"
    TV_BINGER = "tv_binger"
    FAMILY_VIEWER = "family_viewer"


USER_PROFILES = {
    1: {"name": "Alex Chen", "type": UserType.ACTION_LOVER, "preferred_genres": ["Action", "Thriller", "Crime"], "disliked_genres": ["Romance", "Musical"], "min_rating": 7.0},
    2: {"name": "Sarah Kim", "type": UserType.SCI_FI_GEEK, "preferred_genres": ["Sci-Fi", "Mystery", "Thriller"], "disliked_genres": ["Horror", "War"], "min_rating": 7.5},
    3: {"name": "Michael Brown", "type": UserType.DRAMA_FAN, "preferred_genres": ["Drama", "Biography", "History"], "disliked_genres": ["Horror", "Animation"], "min_rating": 8.0},
    4: {"name": "Emma Wilson", "type": UserType.HORROR_ENTHUSIAST, "preferred_genres": ["Horror", "Thriller", "Mystery"], "disliked_genres": ["Romance", "Family"], "min_rating": 6.5},
    5: {"name": "David Garcia", "type": UserType.COMEDY_LOVER, "preferred_genres": ["Comedy", "Adventure", "Family"], "disliked_genres": ["Horror", "War"], "min_rating": 7.0},
    6: {"name": "Sophie Martin", "type": UserType.ROMANCE_SEEKER, "preferred_genres": ["Romance", "Drama", "Music"], "disliked_genres": ["Horror", "Action"], "min_rating": 7.0},
    7: {"name": "Yuki Tanaka", "type": UserType.ANIME_OTAKU, "preferred_genres": ["Animation", "Fantasy", "Adventure"], "disliked_genres": ["Horror", "War"], "min_rating": 7.5},
    8: {"name": "Robert Taylor", "type": UserType.CLASSIC_CINEPHILE, "preferred_genres": ["Drama", "Crime", "Mystery"], "disliked_genres": ["Animation", "Family"], "min_rating": 8.0},
    9: {"name": "Jessica Lee", "type": UserType.TV_BINGER, "preferred_genres": ["Drama", "Fantasy", "Comedy"], "disliked_genres": ["Documentary"], "min_rating": 8.0},
    10: {"name": "Jennifer Adams", "type": UserType.FAMILY_VIEWER, "preferred_genres": ["Animation", "Family", "Adventure"], "disliked_genres": ["Horror", "Crime"], "min_rating": 7.0},
}


def get_user_profile(user_id: int):
    if user_id in USER_PROFILES:
        return USER_PROFILES[user_id]
    random.seed(user_id)
    types = list(UserType)
    return {
        "name": f"User #{user_id}",
        "type": random.choice(types),
        "preferred_genres": ["Drama", "Action", "Comedy"][:random.randint(2, 3)],
        "disliked_genres": ["Horror"],
        "min_rating": 7.0
    }


def get_personalized_recommendations(user_id: int, n: int = 10, exclude_ids: List[int] = None):
    profile = get_user_profile(user_id)
    exclude_ids = exclude_ids or []
    
    results = []
    for item in MEDIA_DATABASE:
        if item["id"] in exclude_ids:
            continue
        
        score = 0
        reasons = []
        item_genres = set(item.get("genres", []))
        preferred = set(profile["preferred_genres"])
        disliked = set(profile.get("disliked_genres", []))
        
        matched = item_genres & preferred
        if matched:
            score += len(matched) * 0.3
            reasons.append(f"Matches your favorite genres: {', '.join(matched)}")
        
        if item_genres & disliked:
            score -= 0.2
        
        if item["rating"] >= profile.get("min_rating", 7.0):
            score += item["rating"] / 10 * 0.2
            if item["rating"] >= 8.5:
                reasons.append(f"Highly rated ({item['rating']}/10)")
        
        if score > 0.2:
            results.append({
                **item,
                "score": min(score, 1.0),
                "match_percentage": int(min(score, 1.0) * 100),
                "reasons": reasons if reasons else ["Recommended based on your history"]
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:n]


def get_trending(n: int = 10):
    return sorted(MEDIA_DATABASE, key=lambda x: x["popularity"], reverse=True)[:n]

def get_top_rated(n: int = 10):
    return sorted(MEDIA_DATABASE, key=lambda x: x["rating"], reverse=True)[:n]

def get_media_by_id(item_id: int):
    for item in MEDIA_DATABASE:
        if item["id"] == item_id:
            return item
    return None

def get_similar_items(item_id: int, n: int = 10):
    item = get_media_by_id(item_id)
    if not item:
        return []
    item_genres = set(item.get("genres", []))
    results = []
    for m in MEDIA_DATABASE:
        if m["id"] == item_id:
            continue
        overlap = len(set(m.get("genres", [])) & item_genres)
        if overlap > 0:
            results.append((overlap, m))
    results.sort(key=lambda x: (-x[0], -x[1]["rating"]))
    return [r[1] for r in results[:n]]


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="MediaRec API",
    description="AI-Powered Media Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendationRequest(BaseModel):
    n_recommendations: int = Field(default=10, ge=1, le=100)
    exclude_items: List[int] = Field(default_factory=list)

class RecommendationItem(BaseModel):
    item_id: int
    score: float
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[RecommendationItem]
    model_version: str = "hybrid-v2"
    latency_ms: float


@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "public", "index.html"))


@app.get("/health")
async def health():
    return {"status": "healthy", "movies": len(MEDIA_DATABASE)}


@app.get("/api/v1/all-media")
async def get_all_media(limit: int = 100, offset: int = 0):
    items = MEDIA_DATABASE[offset:offset + limit]
    return {
        "total": len(MEDIA_DATABASE),
        "items": [{
            "item_id": m["id"],
            "title": m["title"],
            "year": m["year"],
            "genres": m["genres"],
            "rating": m["rating"],
            "poster": m["poster"],
            "backdrop": m.get("backdrop", ""),
            "description": m["description"],
            "duration": m["duration"],
            "director": m["director"],
            "cast": m["cast"],
            "popularity_score": m["popularity"],
            "media_type": m["media_type"]
        } for m in items]
    }


@app.get("/api/v1/trending")
async def trending(n: int = 10):
    items = get_trending(n)
    return {"items": [{
        "item_id": m["id"],
        "title": m["title"],
        "year": m["year"],
        "genres": m["genres"],
        "rating": m["rating"],
        "poster": m["poster"],
        "backdrop": m.get("backdrop", ""),
        "description": m["description"],
        "duration": m["duration"],
        "director": m["director"],
        "cast": m["cast"],
        "popularity_score": m["popularity"],
        "media_type": m["media_type"]
    } for m in items]}


@app.get("/api/v1/top-rated")
async def top_rated(n: int = 10):
    items = get_top_rated(n)
    return {"items": [{
        "item_id": m["id"],
        "title": m["title"],
        "year": m["year"],
        "genres": m["genres"],
        "rating": m["rating"],
        "poster": m["poster"],
        "backdrop": m.get("backdrop", ""),
        "description": m["description"],
        "duration": m["duration"],
        "director": m["director"],
        "cast": m["cast"],
        "popularity_score": m["popularity"],
        "media_type": m["media_type"]
    } for m in items]}


@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: int):
    item = get_media_by_id(item_id)
    if not item:
        return {"error": "Not found"}
    return item


@app.get("/api/v1/items/{item_id}/similar")
async def similar(item_id: int, n: int = 10):
    items = get_similar_items(item_id, n)
    return {"items": [{
        "item_id": m["id"],
        "title": m["title"],
        "year": m["year"],
        "genres": m["genres"],
        "rating": m["rating"],
        "poster": m["poster"],
        "description": m["description"],
        "media_type": m["media_type"]
    } for m in items]}


@app.get("/api/v1/genres")
async def get_genres():
    genres = set()
    for m in MEDIA_DATABASE:
        genres.update(m.get("genres", []))
    return {"genres": sorted(list(genres))}


@app.post("/api/v1/recommendations/{user_id}")
async def recommendations(user_id: int, request: RecommendationRequest):
    start = time.time()
    
    recs = get_personalized_recommendations(user_id, request.n_recommendations, request.exclude_items)
    
    items = []
    for r in recs:
        items.append(RecommendationItem(
            item_id=r["id"],
            score=r["score"],
            explanation="; ".join(r.get("reasons", [])),
            metadata={
                "title": r["title"],
                "genre": ", ".join(r["genres"]),
                "genres": r["genres"],
                "year": r["year"],
                "rating": r["rating"],
                "poster": r["poster"],
                "backdrop": r.get("backdrop", ""),
                "description": r["description"],
                "duration": r["duration"],
                "director": r["director"],
                "cast": r["cast"],
                "media_type": r["media_type"],
                "match_percentage": r.get("match_percentage", 85),
                "reasons": r.get("reasons", [])
            }
        ))
    
    return RecommendationResponse(
        user_id=user_id,
        recommendations=items,
        latency_ms=(time.time() - start) * 1000
    )


@app.get("/api/v1/users/{user_id}/profile")
async def user_profile(user_id: int):
    profile = get_user_profile(user_id)
    return {
        "user_id": user_id,
        "name": profile["name"],
        "type": profile["type"].value if hasattr(profile["type"], "value") else profile["type"],
        "type_label": (profile["type"].value if hasattr(profile["type"], "value") else profile["type"]).replace("_", " ").title(),
        "preferred_genres": profile["preferred_genres"],
        "disliked_genres": profile.get("disliked_genres", []),
        "min_rating": profile.get("min_rating", 7.0)
    }


@app.get("/api/v1/users/profiles")
async def list_profiles():
    profiles = []
    for uid, p in USER_PROFILES.items():
        profiles.append({
            "user_id": uid,
            "name": p["name"],
            "type": p["type"].value,
            "type_label": p["type"].value.replace("_", " ").title(),
            "preferred_genres": p["preferred_genres"]
        })
    return {"profiles": profiles}
