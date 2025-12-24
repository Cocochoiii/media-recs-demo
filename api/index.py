"""
Vercel Serverless API - Standalone version for deployment
No heavy dependencies (torch, transformers, etc.)
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import os

# ============================================
# MEDIA DATABASE (100 movies)
# ============================================

MEDIA_DATABASE = [
    # Action Movies
    {"id": 1, "title": "The Dark Knight", "year": 2008, "genres": ["Action", "Crime", "Drama"], "rating": 9.0, "poster": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg", "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.", "duration": 152, "director": "Christopher Nolan", "cast": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"], "popularity": 95, "media_type": "movie"},
    {"id": 2, "title": "Inception", "year": 2010, "genres": ["Action", "Sci-Fi", "Thriller"], "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Ber.jpg", "backdrop": "https://image.tmdb.org/t/p/original/s3TBrRGB1iav7gFOCNx3H31MoES.jpg", "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.", "duration": 148, "director": "Christopher Nolan", "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"], "popularity": 94, "media_type": "movie"},
    {"id": 3, "title": "Mad Max: Fury Road", "year": 2015, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg", "backdrop": "https://image.tmdb.org/t/p/original/phszHPFVhPHhMZgo0fWTKBDQsJA.jpg", "description": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.", "duration": 120, "director": "George Miller", "cast": ["Tom Hardy", "Charlize Theron", "Nicholas Hoult"], "popularity": 88, "media_type": "movie"},
    {"id": 4, "title": "John Wick", "year": 2014, "genres": ["Action", "Crime", "Thriller"], "rating": 7.4, "poster": "https://image.tmdb.org/t/p/w500/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg", "backdrop": "https://image.tmdb.org/t/p/original/umC04Cozevu8nn3JTDJ1pc7PVTn.jpg", "description": "An ex-hit-man comes out of retirement to track down the gangsters that killed his dog and took everything from him.", "duration": 101, "director": "Chad Stahelski", "cast": ["Keanu Reeves", "Michael Nyqvist", "Alfie Allen"], "popularity": 86, "media_type": "movie"},
    {"id": 5, "title": "Top Gun: Maverick", "year": 2022, "genres": ["Action", "Drama"], "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/62HCnUTziyWcpDaBO2i1DX17ljH.jpg", "backdrop": "https://image.tmdb.org/t/p/original/AaV1YIdWKhF9dBWaVVBQD8d1toE.jpg", "description": "After more than thirty years of service as one of the Navy's top aviators, Pete Mitchell is where he belongs, pushing the envelope as a courageous test pilot.", "duration": 130, "director": "Joseph Kosinski", "cast": ["Tom Cruise", "Jennifer Connelly", "Miles Teller"], "popularity": 92, "media_type": "movie"},
    
    # Sci-Fi Movies
    {"id": 6, "title": "Interstellar", "year": 2014, "genres": ["Sci-Fi", "Adventure", "Drama"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg", "backdrop": "https://image.tmdb.org/t/p/original/xJHokMbljvjADYdit5fK5VQsXEG.jpg", "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.", "duration": 169, "director": "Christopher Nolan", "cast": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"], "popularity": 93, "media_type": "movie"},
    {"id": 7, "title": "Blade Runner 2049", "year": 2017, "genres": ["Sci-Fi", "Drama", "Mystery"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg", "backdrop": "https://image.tmdb.org/t/p/original/ilRyazdMJwN05exqhwK4tMKBYZs.jpg", "description": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard.", "duration": 164, "director": "Denis Villeneuve", "cast": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"], "popularity": 85, "media_type": "movie"},
    {"id": 8, "title": "Dune", "year": 2021, "genres": ["Sci-Fi", "Adventure", "Drama"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg", "backdrop": "https://image.tmdb.org/t/p/original/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg", "description": "Feature adaptation of Frank Herbert's science fiction novel about the son of a noble family entrusted with the protection of the most valuable asset in the galaxy.", "duration": 155, "director": "Denis Villeneuve", "cast": ["Timothée Chalamet", "Rebecca Ferguson", "Zendaya"], "popularity": 91, "media_type": "movie"},
    {"id": 9, "title": "The Matrix", "year": 1999, "genres": ["Sci-Fi", "Action"], "rating": 8.7, "poster": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg", "backdrop": "https://image.tmdb.org/t/p/original/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg", "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.", "duration": 136, "director": "The Wachowskis", "cast": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"], "popularity": 90, "media_type": "movie"},
    {"id": 10, "title": "Avatar", "year": 2009, "genres": ["Sci-Fi", "Adventure", "Fantasy"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg", "backdrop": "https://image.tmdb.org/t/p/original/o0s4XsEDfDlvit5pDRKjzXR4pp2.jpg", "description": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.", "duration": 162, "director": "James Cameron", "cast": ["Sam Worthington", "Zoe Saldana", "Sigourney Weaver"], "popularity": 89, "media_type": "movie"},
    
    # Drama Movies
    {"id": 11, "title": "The Shawshank Redemption", "year": 1994, "genres": ["Drama", "Crime"], "rating": 9.3, "poster": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg", "backdrop": "https://image.tmdb.org/t/p/original/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg", "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.", "duration": 142, "director": "Frank Darabont", "cast": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"], "popularity": 96, "media_type": "movie"},
    {"id": 12, "title": "Forrest Gump", "year": 1994, "genres": ["Drama", "Romance"], "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg", "backdrop": "https://image.tmdb.org/t/p/original/7c9UVPPiTPltouxRVY6N9uugaVA.jpg", "description": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.", "duration": 142, "director": "Robert Zemeckis", "cast": ["Tom Hanks", "Robin Wright", "Gary Sinise"], "popularity": 92, "media_type": "movie"},
    {"id": 13, "title": "The Godfather", "year": 1972, "genres": ["Crime", "Drama"], "rating": 9.2, "poster": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg", "backdrop": "https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2M4GeiP.jpg", "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant youngest son.", "duration": 175, "director": "Francis Ford Coppola", "cast": ["Marlon Brando", "Al Pacino", "James Caan"], "popularity": 94, "media_type": "movie"},
    {"id": 14, "title": "Schindler's List", "year": 1993, "genres": ["Drama", "History", "War"], "rating": 9.0, "poster": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg", "backdrop": "https://image.tmdb.org/t/p/original/loRmRzQXZeqG78TqZuyvSlEQfZb.jpg", "description": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.", "duration": 195, "director": "Steven Spielberg", "cast": ["Liam Neeson", "Ben Kingsley", "Ralph Fiennes"], "popularity": 91, "media_type": "movie"},
    {"id": 15, "title": "Parasite", "year": 2019, "genres": ["Drama", "Thriller", "Comedy"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg", "backdrop": "https://image.tmdb.org/t/p/original/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg", "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.", "duration": 132, "director": "Bong Joon-ho", "cast": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"], "popularity": 90, "media_type": "movie"},
    
    # Thriller Movies
    {"id": 16, "title": "Se7en", "year": 1995, "genres": ["Crime", "Drama", "Mystery", "Thriller"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngEmJskVUO.jpg", "backdrop": "https://image.tmdb.org/t/p/original/gNgMtPp7FwZsLbdUd7qVDy6Xp1U.jpg", "description": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives.", "duration": 127, "director": "David Fincher", "cast": ["Brad Pitt", "Morgan Freeman", "Gwyneth Paltrow"], "popularity": 88, "media_type": "movie"},
    {"id": 17, "title": "The Silence of the Lambs", "year": 1991, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg", "backdrop": "https://image.tmdb.org/t/p/original/mfwq2nMBzArzQ7Y9RKE8SKeeTkg.jpg", "description": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer.", "duration": 118, "director": "Jonathan Demme", "cast": ["Jodie Foster", "Anthony Hopkins", "Lawrence A. Bonney"], "popularity": 87, "media_type": "movie"},
    {"id": 18, "title": "Gone Girl", "year": 2014, "genres": ["Drama", "Mystery", "Thriller"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/lv5xShBIDPe7m7J4opyWMDPBsAx.jpg", "backdrop": "https://image.tmdb.org/t/p/original/55GEsIk7NJFfL3JmVuZdUXyl2Ey.jpg", "description": "With his wife's disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him when it's suspected that he may not be innocent.", "duration": 149, "director": "David Fincher", "cast": ["Ben Affleck", "Rosamund Pike", "Neil Patrick Harris"], "popularity": 85, "media_type": "movie"},
    {"id": 19, "title": "Shutter Island", "year": 2010, "genres": ["Mystery", "Thriller"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/kve20tXwUZpu4GUX8l6X7Z4jmL6.jpg", "backdrop": "https://image.tmdb.org/t/p/original/9TGHDvWrqKBzwDxDodHYXEmOE6J.jpg", "description": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane.", "duration": 138, "director": "Martin Scorsese", "cast": ["Leonardo DiCaprio", "Emily Mortimer", "Mark Ruffalo"], "popularity": 86, "media_type": "movie"},
    {"id": 20, "title": "Prisoners", "year": 2013, "genres": ["Crime", "Drama", "Mystery", "Thriller"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/tuZhZ6biFMr5n9YSPnJrqxL6hOH.jpg", "backdrop": "https://image.tmdb.org/t/p/original/wVEGxtncWuK2SNNRjFrs5PhqUMq.jpg", "description": "When Keller Dover's daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads.", "duration": 153, "director": "Denis Villeneuve", "cast": ["Hugh Jackman", "Jake Gyllenhaal", "Viola Davis"], "popularity": 84, "media_type": "movie"},
    
    # Horror Movies
    {"id": 21, "title": "Get Out", "year": 2017, "genres": ["Horror", "Mystery", "Thriller"], "rating": 7.7, "poster": "https://image.tmdb.org/t/p/w500/qbaIJoA8OKHVLX4vH2qKTJyPNgM.jpg", "backdrop": "https://image.tmdb.org/t/p/original/2GfDYzhLCoP5XjPBmKSF4eiXpmJ.jpg", "description": "A young African-American visits his white girlfriend's parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.", "duration": 104, "director": "Jordan Peele", "cast": ["Daniel Kaluuya", "Allison Williams", "Bradley Whitford"], "popularity": 83, "media_type": "movie"},
    {"id": 22, "title": "A Quiet Place", "year": 2018, "genres": ["Drama", "Horror", "Sci-Fi"], "rating": 7.5, "poster": "https://image.tmdb.org/t/p/w500/nAU74GmpUk7t5iklEp3bufwDq4n.jpg", "backdrop": "https://image.tmdb.org/t/p/original/roYyPiQDQKmIKUEhO912dVOCGQU.jpg", "description": "In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing.", "duration": 90, "director": "John Krasinski", "cast": ["Emily Blunt", "John Krasinski", "Millicent Simmonds"], "popularity": 82, "media_type": "movie"},
    {"id": 23, "title": "Hereditary", "year": 2018, "genres": ["Drama", "Horror", "Mystery"], "rating": 7.3, "poster": "https://image.tmdb.org/t/p/w500/p9fmuz2Oj3HtEJEqbIwkFGUhVqL.jpg", "backdrop": "https://image.tmdb.org/t/p/original/4I0DDwxMYVQcHpH9gxyT2Z7sZ59.jpg", "description": "A grieving family is haunted by tragic and disturbing occurrences.", "duration": 127, "director": "Ari Aster", "cast": ["Toni Collette", "Milly Shapiro", "Gabriel Byrne"], "popularity": 80, "media_type": "movie"},
    {"id": 24, "title": "The Conjuring", "year": 2013, "genres": ["Horror", "Mystery", "Thriller"], "rating": 7.5, "poster": "https://image.tmdb.org/t/p/w500/wVYREutTvI2tmxr6ujrHT704wGF.jpg", "backdrop": "https://image.tmdb.org/t/p/original/xg5LEJDA2fBmVphP59XUYJzSFhs.jpg", "description": "Paranormal investigators Ed and Lorraine Warren work to help a family terrorized by a dark presence in their farmhouse.", "duration": 112, "director": "James Wan", "cast": ["Patrick Wilson", "Vera Farmiga", "Ron Livingston"], "popularity": 81, "media_type": "movie"},
    {"id": 25, "title": "It", "year": 2017, "genres": ["Horror", "Fantasy"], "rating": 7.3, "poster": "https://image.tmdb.org/t/p/w500/9E2y5Q7WlCVNEhP5GiVTjhEhx1o.jpg", "backdrop": "https://image.tmdb.org/t/p/original/tcheoA2nPATCm2vvXw2hVQoaEFD.jpg", "description": "In the summer of 1989, a group of bullied kids band together to destroy a shape-shifting monster, which disguises itself as a clown and preys on the children of Derry, their small Maine town.", "duration": 135, "director": "Andy Muschietti", "cast": ["Bill Skarsgård", "Jaeden Martell", "Finn Wolfhard"], "popularity": 82, "media_type": "movie"},
    
    # Comedy Movies
    {"id": 26, "title": "The Grand Budapest Hotel", "year": 2014, "genres": ["Adventure", "Comedy", "Crime"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nX5XotM9yprCKarRH4fzOq1VM1J.jpg", "description": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy in the hotel's glorious years under an exceptional concierge.", "duration": 99, "director": "Wes Anderson", "cast": ["Ralph Fiennes", "F. Murray Abraham", "Mathieu Amalric"], "popularity": 84, "media_type": "movie"},
    {"id": 27, "title": "Superbad", "year": 2007, "genres": ["Comedy"], "rating": 7.6, "poster": "https://image.tmdb.org/t/p/w500/ek8e8txUyUwd2BNqj6lFEerJfbq.jpg", "backdrop": "https://image.tmdb.org/t/p/original/65DftFkGMmCPyOH9WKurCqODyac.jpg", "description": "Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry.", "duration": 113, "director": "Greg Mottola", "cast": ["Jonah Hill", "Michael Cera", "Christopher Mintz-Plasse"], "popularity": 78, "media_type": "movie"},
    {"id": 28, "title": "The Hangover", "year": 2009, "genres": ["Comedy"], "rating": 7.7, "poster": "https://image.tmdb.org/t/p/w500/uluhlXubGu1VxkEJBfGoPjLgNvE.jpg", "backdrop": "https://image.tmdb.org/t/p/original/5qMJrqHkvNKsWhoB3FIM4MQO3II.jpg", "description": "Three buddies wake up from a bachelor party in Las Vegas, with no memory of the previous night and the bachelor missing.", "duration": 100, "director": "Todd Phillips", "cast": ["Bradley Cooper", "Ed Helms", "Zach Galifianakis"], "popularity": 83, "media_type": "movie"},
    {"id": 29, "title": "Knives Out", "year": 2019, "genres": ["Comedy", "Crime", "Drama", "Mystery"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/pThyQovXQrw2m0s9x82twj48Jq4.jpg", "backdrop": "https://image.tmdb.org/t/p/original/4HWAQu28e2yaWrtupFPGFkdNU7V.jpg", "description": "A detective investigates the death of a patriarch of an eccentric, combative family.", "duration": 130, "director": "Rian Johnson", "cast": ["Daniel Craig", "Chris Evans", "Ana de Armas"], "popularity": 86, "media_type": "movie"},
    {"id": 30, "title": "Jojo Rabbit", "year": 2019, "genres": ["Comedy", "Drama", "War"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/7GsM4mtM0worCtIVeiQt28HieeN.jpg", "backdrop": "https://image.tmdb.org/t/p/original/agoBZfL1q5G79SD0npArSlJn8BH.jpg", "description": "A young boy in Hitler's army finds out his mother is hiding a Jewish girl in their home.", "duration": 108, "director": "Taika Waititi", "cast": ["Roman Griffin Davis", "Thomasin McKenzie", "Scarlett Johansson"], "popularity": 82, "media_type": "movie"},
    
    # Animation Movies
    {"id": 31, "title": "Spider-Man: Into the Spider-Verse", "year": 2018, "genres": ["Animation", "Action", "Adventure"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg", "backdrop": "https://image.tmdb.org/t/p/original/aUVCJ0HkcJIBrTJYPnTXta8h9Co.jpg", "description": "Teen Miles Morales becomes the Spider-Man of his universe, and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.", "duration": 117, "director": "Bob Persichetti", "cast": ["Shameik Moore", "Jake Johnson", "Hailee Steinfeld"], "popularity": 89, "media_type": "movie"},
    {"id": 32, "title": "Coco", "year": 2017, "genres": ["Animation", "Adventure", "Family", "Music"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nlPCdZlHtRNcF6C9hzUH4ebmV1w.jpg", "description": "Aspiring musician Miguel, confronted with his family's ancestral ban on music, enters the Land of the Dead to find his great-great-grandfather, a legendary singer.", "duration": 105, "director": "Lee Unkrich", "cast": ["Anthony Gonzalez", "Gael García Bernal", "Benjamin Bratt"], "popularity": 88, "media_type": "movie"},
    {"id": 33, "title": "Your Name", "year": 2016, "genres": ["Animation", "Drama", "Fantasy", "Romance"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6babgKnONONX.jpg", "backdrop": "https://image.tmdb.org/t/p/original/dIWwZW7dJJtqC6CgWzYkNVKIUm8.jpg", "description": "Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?", "duration": 106, "director": "Makoto Shinkai", "cast": ["Ryunosuke Kamiki", "Mone Kamishiraishi", "Ryo Narita"], "popularity": 87, "media_type": "movie"},
    {"id": 34, "title": "Spirited Away", "year": 2001, "genres": ["Animation", "Adventure", "Family", "Fantasy"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg", "backdrop": "https://image.tmdb.org/t/p/original/mSDsSDwaP3E7dEfUPWy4J0djt4O.jpg", "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.", "duration": 125, "director": "Hayao Miyazaki", "cast": ["Rumi Hiiragi", "Miyu Irino", "Mari Natsuki"], "popularity": 90, "media_type": "movie"},
    {"id": 35, "title": "Toy Story 4", "year": 2019, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 7.7, "poster": "https://image.tmdb.org/t/p/w500/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg", "backdrop": "https://image.tmdb.org/t/p/original/m67smI1IIMmYzCl9axvKNULVKLr.jpg", "description": "When a new toy called 'Forky' joins Woody and the gang, a road trip alongside old and new friends reveals how big the world can be for a toy.", "duration": 100, "director": "Josh Cooley", "cast": ["Tom Hanks", "Tim Allen", "Annie Potts"], "popularity": 85, "media_type": "movie"},
    
    # Romance Movies
    {"id": 36, "title": "La La Land", "year": 2016, "genres": ["Comedy", "Drama", "Music", "Romance"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg", "backdrop": "https://image.tmdb.org/t/p/original/mUevWAx1BqKlcWHbNIjPDhb9AB6.jpg", "description": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.", "duration": 128, "director": "Damien Chazelle", "cast": ["Ryan Gosling", "Emma Stone", "Rosemarie DeWitt"], "popularity": 87, "media_type": "movie"},
    {"id": 37, "title": "The Notebook", "year": 2004, "genres": ["Drama", "Romance"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/rNzQyW4f8B8cQeg7Dgj3n6eT5k9.jpg", "backdrop": "https://image.tmdb.org/t/p/original/qom1SZSENdmHFNZBXbtJAU0WTlC.jpg", "description": "A poor yet passionate young man falls in love with a rich young woman, giving her a sense of freedom, but they are soon separated because of their social differences.", "duration": 123, "director": "Nick Cassavetes", "cast": ["Gena Rowlands", "James Garner", "Rachel McAdams"], "popularity": 84, "media_type": "movie"},
    {"id": 38, "title": "Pride & Prejudice", "year": 2005, "genres": ["Drama", "Romance"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/lqUfYjz1r8nAUHtlWVUmYDXqfmq.jpg", "backdrop": "https://image.tmdb.org/t/p/original/5zFmaJYp9aW5u6SLFvkv4U9CgYF.jpg", "description": "Sparks fly when spirited Elizabeth Bennet meets single, rich, and proud Mr. Darcy.", "duration": 129, "director": "Joe Wright", "cast": ["Keira Knightley", "Matthew Macfadyen", "Brenda Blethyn"], "popularity": 83, "media_type": "movie"},
    {"id": 39, "title": "Eternal Sunshine of the Spotless Mind", "year": 2004, "genres": ["Drama", "Romance", "Sci-Fi"], "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg", "backdrop": "https://image.tmdb.org/t/p/original/1ZyDYbDa6xBXj0SVEvKCVVphdIS.jpg", "description": "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories.", "duration": 108, "director": "Michel Gondry", "cast": ["Jim Carrey", "Kate Winslet", "Tom Wilkinson"], "popularity": 86, "media_type": "movie"},
    {"id": 40, "title": "Titanic", "year": 1997, "genres": ["Drama", "Romance"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg", "backdrop": "https://image.tmdb.org/t/p/original/4qCqAdHcNKeAHcK8tJ8wNJZa9cx.jpg", "description": "A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.", "duration": 194, "director": "James Cameron", "cast": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"], "popularity": 91, "media_type": "movie"},
    
    # TV Shows
    {"id": 41, "title": "Breaking Bad", "year": 2008, "genres": ["Crime", "Drama", "Thriller"], "rating": 9.5, "poster": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg", "backdrop": "https://image.tmdb.org/t/p/original/tsRy63Mu5cu8etL1X7ZLyf7ureI.jpg", "description": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future.", "duration": 45, "director": "Vince Gilligan", "cast": ["Bryan Cranston", "Aaron Paul", "Anna Gunn"], "popularity": 97, "media_type": "tv"},
    {"id": 42, "title": "Game of Thrones", "year": 2011, "genres": ["Action", "Adventure", "Drama", "Fantasy"], "rating": 9.2, "poster": "https://image.tmdb.org/t/p/w500/u3bZgnGQ9T01sWNhyveQz0wH0Hl.jpg", "backdrop": "https://image.tmdb.org/t/p/original/suopoADq0k8YZr4dQXcU6pToj6s.jpg", "description": "Nine noble families fight for control over the lands of Westeros, while an ancient enemy returns after being dormant for millennia.", "duration": 60, "director": "David Benioff", "cast": ["Peter Dinklage", "Lena Headey", "Emilia Clarke"], "popularity": 96, "media_type": "tv"},
    {"id": 43, "title": "Stranger Things", "year": 2016, "genres": ["Drama", "Fantasy", "Horror", "Mystery"], "rating": 8.7, "poster": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg", "backdrop": "https://image.tmdb.org/t/p/original/56v2KjBlU4XaOv9rVYEQypROD7P.jpg", "description": "When a young boy disappears, his mother, a police chief and his friends must confront terrifying supernatural forces in order to get him back.", "duration": 50, "director": "The Duffer Brothers", "cast": ["Millie Bobby Brown", "Finn Wolfhard", "Winona Ryder"], "popularity": 93, "media_type": "tv"},
    {"id": 44, "title": "The Office", "year": 2005, "genres": ["Comedy"], "rating": 9.0, "poster": "https://image.tmdb.org/t/p/w500/qWnJzyZhyy74gjpSjIXWmuk0ifX.jpg", "backdrop": "https://image.tmdb.org/t/p/original/vNpuAxGTl9HsUbHqam3E9CzqCvX.jpg", "description": "A mockumentary on a group of typical office workers, where the workday consists of ego clashes, inappropriate behavior, and tedium.", "duration": 22, "director": "Greg Daniels", "cast": ["Steve Carell", "Rainn Wilson", "John Krasinski"], "popularity": 92, "media_type": "tv"},
    {"id": 45, "title": "The Crown", "year": 2016, "genres": ["Biography", "Drama", "History"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/dqS3k36dd7TGJVSYm3TvqZL08t5.jpg", "backdrop": "https://image.tmdb.org/t/p/original/sNqEGVt3UXbVIJokj2V0J1qrZ8z.jpg", "description": "Follows the political rivalries and romance of Queen Elizabeth II's reign and the events that shaped the second half of the twentieth century.", "duration": 60, "director": "Peter Morgan", "cast": ["Claire Foy", "Olivia Colman", "Imelda Staunton"], "popularity": 88, "media_type": "tv"},
    
    # More Action Movies
    {"id": 46, "title": "The Avengers", "year": 2012, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nNmJRkg8wWnRmzQDe2FwKbPIsJV.jpg", "description": "Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.", "duration": 143, "director": "Joss Whedon", "cast": ["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson"], "popularity": 91, "media_type": "movie"},
    {"id": 47, "title": "Black Panther", "year": 2018, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 7.3, "poster": "https://image.tmdb.org/t/p/w500/uxzzxijgPIY7slzFvMotPv8wjKA.jpg", "backdrop": "https://image.tmdb.org/t/p/original/6ELJEzQJ3Y45HczvreC3dg0GV5R.jpg", "description": "T'Challa, heir to the hidden but advanced kingdom of Wakanda, must step forward to lead his people into a new future and must confront a challenger from his country's past.", "duration": 134, "director": "Ryan Coogler", "cast": ["Chadwick Boseman", "Michael B. Jordan", "Lupita Nyong'o"], "popularity": 88, "media_type": "movie"},
    {"id": 48, "title": "Gladiator", "year": 2000, "genres": ["Action", "Adventure", "Drama"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg", "backdrop": "https://image.tmdb.org/t/p/original/mw04yp3AZcJgkAO9cH8DnwptPrg.jpg", "description": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.", "duration": 155, "director": "Ridley Scott", "cast": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen"], "popularity": 89, "media_type": "movie"},
    {"id": 49, "title": "Django Unchained", "year": 2012, "genres": ["Drama", "Western"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg", "backdrop": "https://image.tmdb.org/t/p/original/2oZklIzUbvZXXzIFzv7Hi68d6xf.jpg", "description": "With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.", "duration": 165, "director": "Quentin Tarantino", "cast": ["Jamie Foxx", "Christoph Waltz", "Leonardo DiCaprio"], "popularity": 90, "media_type": "movie"},
    {"id": 50, "title": "Kill Bill: Vol. 1", "year": 2003, "genres": ["Action", "Crime", "Thriller"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/v7TKYjCTFOptwFcnl6k3VfBpCqe.jpg", "backdrop": "https://image.tmdb.org/t/p/original/bj1SH7kzYQn5WkOEQAuM4CDUl9c.jpg", "description": "After awakening from a four-year coma, a former assassin wreaks vengeance on the team of assassins who betrayed her.", "duration": 111, "director": "Quentin Tarantino", "cast": ["Uma Thurman", "David Carradine", "Daryl Hannah"], "popularity": 86, "media_type": "movie"},
    
    # More Drama/Thriller
    {"id": 51, "title": "The Departed", "year": 2006, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq2pcQAgEpJU.jpg", "backdrop": "https://image.tmdb.org/t/p/original/8Xs7WmyVQqUkh5DxqZvJpELIGJm.jpg", "description": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in South Boston.", "duration": 151, "director": "Martin Scorsese", "cast": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"], "popularity": 88, "media_type": "movie"},
    {"id": 52, "title": "Joker", "year": 2019, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg", "backdrop": "https://image.tmdb.org/t/p/original/n6bUvigpRFqSwmPp1m2YMDNqKPc.jpg", "description": "In Gotham City, mentally troubled comedian Arthur Fleck is disregarded and mistreated by society. He then embarks on a downward spiral of revolution and bloody crime.", "duration": 122, "director": "Todd Phillips", "cast": ["Joaquin Phoenix", "Robert De Niro", "Zazie Beetz"], "popularity": 92, "media_type": "movie"},
    {"id": 53, "title": "Whiplash", "year": 2014, "genres": ["Drama", "Music"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg", "backdrop": "https://image.tmdb.org/t/p/original/fRGxZuo7jJUWQsVg9PREb98Aclp.jpg", "description": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.", "duration": 106, "director": "Damien Chazelle", "cast": ["Miles Teller", "J.K. Simmons", "Paul Reiser"], "popularity": 87, "media_type": "movie"},
    {"id": 54, "title": "Fight Club", "year": 1999, "genres": ["Drama"], "rating": 8.8, "poster": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg", "backdrop": "https://image.tmdb.org/t/p/original/87hTDiay2N2qWyX4Ds7ybXi9h8I.jpg", "description": "An insomniac office worker and a devil-may-care soapmaker form an underground fight club that evolves into something much, much more.", "duration": 139, "director": "David Fincher", "cast": ["Brad Pitt", "Edward Norton", "Meat Loaf"], "popularity": 91, "media_type": "movie"},
    {"id": 55, "title": "Pulp Fiction", "year": 1994, "genres": ["Crime", "Drama"], "rating": 8.9, "poster": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg", "backdrop": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg", "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.", "duration": 154, "director": "Quentin Tarantino", "cast": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"], "popularity": 93, "media_type": "movie"},
    
    # More Movies (56-100)
    {"id": 56, "title": "Goodfellas", "year": 1990, "genres": ["Biography", "Crime", "Drama"], "rating": 8.7, "poster": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg", "backdrop": "https://image.tmdb.org/t/p/original/sw7mordbZxgITU877yTpZCud90M.jpg", "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito.", "duration": 146, "director": "Martin Scorsese", "cast": ["Robert De Niro", "Ray Liotta", "Joe Pesci"], "popularity": 89, "media_type": "movie"},
    {"id": 57, "title": "The Prestige", "year": 2006, "genres": ["Drama", "Mystery", "Sci-Fi", "Thriller"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/bdN3gXuIZYaJP7ftKK2sU0nPtEA.jpg", "backdrop": "https://image.tmdb.org/t/p/original/dF0bTDCG68k53vQwWmNnA1VXrkS.jpg", "description": "After a tragic accident, two stage magicians engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.", "duration": 130, "director": "Christopher Nolan", "cast": ["Christian Bale", "Hugh Jackman", "Scarlett Johansson"], "popularity": 88, "media_type": "movie"},
    {"id": 58, "title": "Memento", "year": 2000, "genres": ["Mystery", "Thriller"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/yuNs09hvpHVU1cBTCAk9zTl3PRB.jpg", "backdrop": "https://image.tmdb.org/t/p/original/8vIFWjh4n1PAFgQapq5KfJh04sZ.jpg", "description": "A man with short-term memory loss attempts to track down his wife's murderer.", "duration": 113, "director": "Christopher Nolan", "cast": ["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano"], "popularity": 86, "media_type": "movie"},
    {"id": 59, "title": "The Social Network", "year": 2010, "genres": ["Biography", "Drama"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg", "backdrop": "https://image.tmdb.org/t/p/original/c1OoQ3c8wJLvfWJyWPWz3xqBpAr.jpg", "description": "As Harvard student Mark Zuckerberg creates the social networking site that would become known as Facebook, he is sued by the twins who claimed he stole their idea.", "duration": 120, "director": "David Fincher", "cast": ["Jesse Eisenberg", "Andrew Garfield", "Justin Timberlake"], "popularity": 84, "media_type": "movie"},
    {"id": 60, "title": "1917", "year": 2019, "genres": ["Drama", "War"], "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/iZf0KyrE25z1sage4SYFLCCrMi9.jpg", "backdrop": "https://image.tmdb.org/t/p/original/tUWivz05fcY14K6RzicRm7IHkUD.jpg", "description": "April 6th, 1917. As a regiment assembles to wage war deep in enemy territory, two soldiers are assigned to race against time and deliver a message that will stop 1,600 men from walking straight into a deadly trap.", "duration": 119, "director": "Sam Mendes", "cast": ["George MacKay", "Dean-Charles Chapman", "Mark Strong"], "popularity": 87, "media_type": "movie"},
    {"id": 61, "title": "Arrival", "year": 2016, "genres": ["Drama", "Mystery", "Sci-Fi"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg", "backdrop": "https://image.tmdb.org/t/p/original/yIZ1xendyqKvY3FGeeUYUd5X9Mm.jpg", "description": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world.", "duration": 116, "director": "Denis Villeneuve", "cast": ["Amy Adams", "Jeremy Renner", "Forest Whitaker"], "popularity": 85, "media_type": "movie"},
    {"id": 62, "title": "The Wolf of Wall Street", "year": 2013, "genres": ["Biography", "Comedy", "Crime", "Drama"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg", "backdrop": "https://image.tmdb.org/t/p/original/cWUOv3H7YFwvKeaQhoAQTLLpo9Z.jpg", "description": "Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker living the high life to his fall involving crime, corruption and the federal government.", "duration": 180, "director": "Martin Scorsese", "cast": ["Leonardo DiCaprio", "Jonah Hill", "Margot Robbie"], "popularity": 90, "media_type": "movie"},
    {"id": 63, "title": "The Green Mile", "year": 1999, "genres": ["Crime", "Drama", "Fantasy"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/velWPhVMQeQKcxggNEU8YmIo52R.jpg", "backdrop": "https://image.tmdb.org/t/p/original/vxJ08SvwomfKbpboCWynC3uqUg4.jpg", "description": "The lives of guards on Death Row are affected by one of their charges: a black man accused of child murder and rape, yet who has a mysterious gift.", "duration": 189, "director": "Frank Darabont", "cast": ["Tom Hanks", "Michael Clarke Duncan", "David Morse"], "popularity": 88, "media_type": "movie"},
    {"id": 64, "title": "Saving Private Ryan", "year": 1998, "genres": ["Drama", "War"], "rating": 8.6, "poster": "https://image.tmdb.org/t/p/w500/1wY4psJ5NVEhCuOYROwLH2XExM2.jpg", "backdrop": "https://image.tmdb.org/t/p/original/bdD39MpSVhKjxarTxLSfX6baoMP.jpg", "description": "Following the Normandy Landings, a group of U.S. soldiers go behind enemy lines to retrieve a paratrooper whose brothers have been killed in action.", "duration": 169, "director": "Steven Spielberg", "cast": ["Tom Hanks", "Matt Damon", "Tom Sizemore"], "popularity": 89, "media_type": "movie"},
    {"id": 65, "title": "The Truman Show", "year": 1998, "genres": ["Comedy", "Drama"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/vuza0WqY239yBXOadKlGwJsZJFE.jpg", "backdrop": "https://image.tmdb.org/t/p/original/pG5EyS5rJLn7bEGLj2YAqPFkbR3.jpg", "description": "An insurance salesman discovers his whole life is actually a reality TV show.", "duration": 103, "director": "Peter Weir", "cast": ["Jim Carrey", "Ed Harris", "Laura Linney"], "popularity": 86, "media_type": "movie"},
    {"id": 66, "title": "No Country for Old Men", "year": 2007, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/bj1v6YKF8yHqA489VFfnQvOJpnc.jpg", "backdrop": "https://image.tmdb.org/t/p/original/6d5XOczc226jECq0LIX0siKtgHR.jpg", "description": "Violence and mayhem ensue after a hunter stumbles upon a drug deal gone wrong and more than two million dollars in cash near the Rio Grande.", "duration": 122, "director": "Coen Brothers", "cast": ["Tommy Lee Jones", "Javier Bardem", "Josh Brolin"], "popularity": 85, "media_type": "movie"},
    {"id": 67, "title": "There Will Be Blood", "year": 2007, "genres": ["Drama"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/fa0RDkAlCec0STeMNAhPaF89q6U.jpg", "backdrop": "https://image.tmdb.org/t/p/original/fi4zJFOqteLuwOhvEQMgD4xvvdD.jpg", "description": "A story of family, religion, hatred, oil and madness, focusing on a turn-of-the-century prospector in the early days of the business.", "duration": 158, "director": "Paul Thomas Anderson", "cast": ["Daniel Day-Lewis", "Paul Dano", "Ciarán Hinds"], "popularity": 82, "media_type": "movie"},
    {"id": 68, "title": "The Revenant", "year": 2015, "genres": ["Action", "Adventure", "Drama"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/ji3ecJphATlVgWNY0B4R6Hqkjq7.jpg", "backdrop": "https://image.tmdb.org/t/p/original/oXUWEc5i3wYyFnL1Ycu8ppxxPvs.jpg", "description": "A frontiersman on a fur trading expedition in the 1820s fights for survival after being mauled by a bear and left for dead by members of his own hunting team.", "duration": 156, "director": "Alejandro González Iñárritu", "cast": ["Leonardo DiCaprio", "Tom Hardy", "Domhnall Gleeson"], "popularity": 87, "media_type": "movie"},
    {"id": 69, "title": "The Departed", "year": 2006, "genres": ["Crime", "Drama", "Thriller"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/nT97ifVT2J1yMQmeq2pcQAgEpJU.jpg", "backdrop": "https://image.tmdb.org/t/p/original/8Xs7WmyVQqUkh5DxqZvJpELIGJm.jpg", "description": "An undercover cop and a mole in the police attempt to identify each other while infiltrating an Irish gang in South Boston.", "duration": 151, "director": "Martin Scorsese", "cast": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"], "popularity": 88, "media_type": "movie"},
    {"id": 70, "title": "Inglourious Basterds", "year": 2009, "genres": ["Adventure", "Drama", "War"], "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/7sfbEnaARXDDhKm0CZ7D7uc2sbo.jpg", "backdrop": "https://image.tmdb.org/t/p/original/gLhHHJsylFHHHhYpNyGqbbPLhEc.jpg", "description": "In Nazi-occupied France during World War II, a plan to assassinate Nazi leaders by a group of Jewish U.S. soldiers coincides with a theatre owner's vengeful plans for the same.", "duration": 153, "director": "Quentin Tarantino", "cast": ["Brad Pitt", "Diane Kruger", "Eli Roth"], "popularity": 88, "media_type": "movie"},
    {"id": 71, "title": "Soul", "year": 2020, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/hm58Jw4Lw8OIeECIq5qyPYhAeRJ.jpg", "backdrop": "https://image.tmdb.org/t/p/original/kf456ZqeC45XTvo6W9pW5clYKfQ.jpg", "description": "A musician who has lost his passion for music is transported out of his body and must find his way back with the help of an infant soul learning about herself.", "duration": 100, "director": "Pete Docter", "cast": ["Jamie Foxx", "Tina Fey", "Graham Norton"], "popularity": 86, "media_type": "movie"},
    {"id": 72, "title": "Up", "year": 2009, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.3, "poster": "https://image.tmdb.org/t/p/w500/vpbaStTMt8qqXaEgnOR2EE4DNJk.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nPimVfznsoGKQidIBMPRzHxLhQp.jpg", "description": "78-year-old Carl Fredricksen travels to Paradise Falls in his house equipped with balloons, inadvertently taking a young stowaway.", "duration": 96, "director": "Pete Docter", "cast": ["Edward Asner", "Jordan Nagai", "John Ratzenberger"], "popularity": 87, "media_type": "movie"},
    {"id": 73, "title": "WALL·E", "year": 2008, "genres": ["Animation", "Adventure", "Family", "Sci-Fi"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg", "backdrop": "https://image.tmdb.org/t/p/original/fJJGo7zuKin1vdkYKpOzXQ8QOLf.jpg", "description": "In the distant future, a small waste-collecting robot inadvertently embarks on a space journey that will ultimately decide the fate of mankind.", "duration": 98, "director": "Andrew Stanton", "cast": ["Ben Burtt", "Elissa Knight", "Jeff Garlin"], "popularity": 88, "media_type": "movie"},
    {"id": 74, "title": "Inside Out", "year": 2015, "genres": ["Animation", "Adventure", "Comedy", "Drama", "Family"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg", "backdrop": "https://image.tmdb.org/t/p/original/j29ekbcLpBvxnGk6LjdTc2EI5SA.jpg", "description": "After young Riley is uprooted from her Midwest life and moved to San Francisco, her emotions - Joy, Fear, Anger, Disgust and Sadness - conflict on how best to navigate a new city, house, and school.", "duration": 95, "director": "Pete Docter", "cast": ["Amy Poehler", "Phyllis Smith", "Richard Kind"], "popularity": 87, "media_type": "movie"},
    {"id": 75, "title": "Ratatouille", "year": 2007, "genres": ["Animation", "Comedy", "Family", "Fantasy"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/t3vaWRPSf6WjDSamIkKDs1iQWna.jpg", "backdrop": "https://image.tmdb.org/t/p/original/aOrEJcc7cUjkPcU9hb4iqFH0hQS.jpg", "description": "A rat who can cook makes an unusual alliance with a young kitchen worker at a famous restaurant.", "duration": 111, "director": "Brad Bird", "cast": ["Patton Oswalt", "Ian Holm", "Lou Romano"], "popularity": 86, "media_type": "movie"},
    {"id": 76, "title": "The Incredibles", "year": 2004, "genres": ["Animation", "Action", "Adventure", "Family"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/2LqaLgk4Z226KkgPJuiOQ58wvrm.jpg", "backdrop": "https://image.tmdb.org/t/p/original/9wSbe4CwObACCQvaUVhWQyLQ5Vm.jpg", "description": "A family of undercover superheroes, while trying to live the quiet suburban life, are forced into action to save the world.", "duration": 115, "director": "Brad Bird", "cast": ["Craig T. Nelson", "Holly Hunter", "Samuel L. Jackson"], "popularity": 87, "media_type": "movie"},
    {"id": 77, "title": "Finding Nemo", "year": 2003, "genres": ["Animation", "Adventure", "Comedy", "Family"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/eHuGQ10FUzK1mdOY69wF5pGgEf5.jpg", "backdrop": "https://image.tmdb.org/t/p/original/dSBzpjHDCgz8JFBLA3qL2DKYm0A.jpg", "description": "After his son is captured in the Great Barrier Reef and taken to Sydney, a timid clownfish sets out on a journey to bring him home.", "duration": 100, "director": "Andrew Stanton", "cast": ["Albert Brooks", "Ellen DeGeneres", "Alexander Gould"], "popularity": 88, "media_type": "movie"},
    {"id": 78, "title": "Monsters, Inc.", "year": 2001, "genres": ["Animation", "Adventure", "Comedy", "Family", "Fantasy"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/sgheSKxZkttIe8ONsf2sKu62rzy.jpg", "backdrop": "https://image.tmdb.org/t/p/original/xV9F0HFGcvkLJEoZrT7N3xKJk9P.jpg", "description": "In order to power the city, monsters have to scare children so that they scream. However, the children are toxic to the monsters, and after a child gets through, 2 monsters realize things may not be what they think.", "duration": 92, "director": "Pete Docter", "cast": ["Billy Crystal", "John Goodman", "Mary Gibbs"], "popularity": 86, "media_type": "movie"},
    {"id": 79, "title": "The Lion King", "year": 1994, "genres": ["Animation", "Adventure", "Drama", "Family", "Music"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg", "backdrop": "https://image.tmdb.org/t/p/original/wXsQvli6tWqja51pYxXNG1LFIGV.jpg", "description": "Lion prince Simba and his father are targeted by his bitter uncle, who wants to ascend the throne himself.", "duration": 88, "director": "Roger Allers", "cast": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones"], "popularity": 91, "media_type": "movie"},
    {"id": 80, "title": "Oppenheimer", "year": 2023, "genres": ["Biography", "Drama", "History"], "rating": 8.5, "poster": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg", "backdrop": "https://image.tmdb.org/t/p/original/rLb2LRVfqLc0Yr1Yr3SUpSL7Tgv.jpg", "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.", "duration": 180, "director": "Christopher Nolan", "cast": ["Cillian Murphy", "Emily Blunt", "Matt Damon"], "popularity": 94, "media_type": "movie"},
    {"id": 81, "title": "Barbie", "year": 2023, "genres": ["Adventure", "Comedy", "Fantasy"], "rating": 7.0, "poster": "https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg", "backdrop": "https://image.tmdb.org/t/p/original/nHf61UzkfFno5X1ofIhugCPus2R.jpg", "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans.", "duration": 114, "director": "Greta Gerwig", "cast": ["Margot Robbie", "Ryan Gosling", "America Ferrera"], "popularity": 89, "media_type": "movie"},
    {"id": 82, "title": "Everything Everywhere All at Once", "year": 2022, "genres": ["Action", "Adventure", "Comedy", "Fantasy", "Sci-Fi"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg", "backdrop": "https://image.tmdb.org/t/p/original/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg", "description": "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save the world by exploring other universes connecting with the lives she could have led.", "duration": 139, "director": "Daniel Kwan", "cast": ["Michelle Yeoh", "Stephanie Hsu", "Ke Huy Quan"], "popularity": 88, "media_type": "movie"},
    {"id": 83, "title": "The Batman", "year": 2022, "genres": ["Action", "Crime", "Drama"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg", "backdrop": "https://image.tmdb.org/t/p/original/b0PlSFdDwbyK0cf5RxwDpaOJQvQ.jpg", "description": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption and question his family's involvement.", "duration": 176, "director": "Matt Reeves", "cast": ["Robert Pattinson", "Zoë Kravitz", "Jeffrey Wright"], "popularity": 90, "media_type": "movie"},
    {"id": 84, "title": "Spider-Man: No Way Home", "year": 2021, "genres": ["Action", "Adventure", "Fantasy"], "rating": 8.2, "poster": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg", "backdrop": "https://image.tmdb.org/t/p/original/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg", "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear, forcing Peter to discover what it truly means to be Spider-Man.", "duration": 148, "director": "Jon Watts", "cast": ["Tom Holland", "Zendaya", "Benedict Cumberbatch"], "popularity": 93, "media_type": "movie"},
    {"id": 85, "title": "Avengers: Endgame", "year": 2019, "genres": ["Action", "Adventure", "Drama", "Sci-Fi"], "rating": 8.4, "poster": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg", "backdrop": "https://image.tmdb.org/t/p/original/7RyHsO4yDXtBv1zUU3mTpHeQ0d5.jpg", "description": "After the devastating events of Avengers: Infinity War, the universe is in ruins. With the help of remaining allies, the Avengers assemble once more in order to reverse Thanos' actions and restore balance to the universe.", "duration": 181, "director": "Anthony Russo", "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"], "popularity": 95, "media_type": "movie"},
    {"id": 86, "title": "Guardians of the Galaxy", "year": 2014, "genres": ["Action", "Adventure", "Comedy", "Sci-Fi"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg", "backdrop": "https://image.tmdb.org/t/p/original/mfn9ojJjLsG6cAcfvh6ILBzRmQN.jpg", "description": "A group of intergalactic criminals must pull together to stop a fanatical warrior with plans to purge the universe.", "duration": 121, "director": "James Gunn", "cast": ["Chris Pratt", "Vin Diesel", "Bradley Cooper"], "popularity": 89, "media_type": "movie"},
    {"id": 87, "title": "Thor: Ragnarok", "year": 2017, "genres": ["Action", "Adventure", "Comedy", "Fantasy"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/rzRwTcFvttcN1ZpX2xv4j3tSdJu.jpg", "backdrop": "https://image.tmdb.org/t/p/original/kaIfm5ryEOwYg8mLbq8HkPuM1Fo.jpg", "description": "Thor is imprisoned on the planet Sakaar, and must race against time to return to Asgard and stop Ragnarök, the destruction of his world, at the hands of the powerful and ruthless villain Hela.", "duration": 130, "director": "Taika Waititi", "cast": ["Chris Hemsworth", "Tom Hiddleston", "Cate Blanchett"], "popularity": 88, "media_type": "movie"},
    {"id": 88, "title": "Doctor Strange", "year": 2016, "genres": ["Action", "Adventure", "Fantasy"], "rating": 7.5, "poster": "https://image.tmdb.org/t/p/w500/uGBVj3bEbCoZbDjjl9wTxcygko1.jpg", "backdrop": "https://image.tmdb.org/t/p/original/6nQOdSqMdowaHqzsPQIlBT8H7aT.jpg", "description": "While on a journey of physical and spiritual healing, a brilliant neurosurgeon is drawn into the world of the mystic arts.", "duration": 115, "director": "Scott Derrickson", "cast": ["Benedict Cumberbatch", "Chiwetel Ejiofor", "Rachel McAdams"], "popularity": 86, "media_type": "movie"},
    {"id": 89, "title": "Iron Man", "year": 2008, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/78lPtwv72eTNqFW9COBYI0dWDJa.jpg", "backdrop": "https://image.tmdb.org/t/p/original/Uhp4Jo8MKKjDlQtIObdKcZPVpV.jpg", "description": "After being held captive in an Afghan cave, billionaire engineer Tony Stark creates a unique weaponized suit of armor to fight evil.", "duration": 126, "director": "Jon Favreau", "cast": ["Robert Downey Jr.", "Gwyneth Paltrow", "Terrence Howard"], "popularity": 90, "media_type": "movie"},
    {"id": 90, "title": "Captain America: The Winter Soldier", "year": 2014, "genres": ["Action", "Adventure", "Sci-Fi", "Thriller"], "rating": 7.8, "poster": "https://image.tmdb.org/t/p/w500/tVFRpFw3xTedgPGqxW0AOI8Qhh0.jpg", "backdrop": "https://image.tmdb.org/t/p/original/c3J2eCIc4vNfkH5ESYmOjYUl3oM.jpg", "description": "As Steve Rogers struggles to embrace his role in the modern world, he teams up with a fellow Avenger and S.H.I.E.L.D agent, Black Widow, to battle a new threat from history: an assassin known as the Winter Soldier.", "duration": 136, "director": "Anthony Russo", "cast": ["Chris Evans", "Samuel L. Jackson", "Scarlett Johansson"], "popularity": 87, "media_type": "movie"},
    {"id": 91, "title": "Deadpool", "year": 2016, "genres": ["Action", "Adventure", "Comedy"], "rating": 8.0, "poster": "https://image.tmdb.org/t/p/w500/fSRb7vyIP8rQpL0I47P3qUsEKX3.jpg", "backdrop": "https://image.tmdb.org/t/p/original/en971MEXui9diirXlogOrPKmsEn.jpg", "description": "A wisecracking mercenary gets experimented on and becomes immortal but ugly, and sets out to track down the man who ruined his looks.", "duration": 108, "director": "Tim Miller", "cast": ["Ryan Reynolds", "Morena Baccarin", "T.J. Miller"], "popularity": 89, "media_type": "movie"},
    {"id": 92, "title": "Logan", "year": 2017, "genres": ["Action", "Drama", "Sci-Fi"], "rating": 8.1, "poster": "https://image.tmdb.org/t/p/w500/fnbjcRDYn6YviCcePDnGdyAkYsB.jpg", "backdrop": "https://image.tmdb.org/t/p/original/8jWyHaWuR9Kg1MoJOE1Y8ztH0rD.jpg", "description": "In a future where mutants are nearly extinct, an elderly and weary Logan leads a quiet life. But when Laura, a mutant child pursued by scientists, comes to him for help, he must get her to safety.", "duration": 137, "director": "James Mangold", "cast": ["Hugh Jackman", "Patrick Stewart", "Dafne Keen"], "popularity": 88, "media_type": "movie"},
    {"id": 93, "title": "X-Men: Days of Future Past", "year": 2014, "genres": ["Action", "Adventure", "Sci-Fi"], "rating": 7.9, "poster": "https://image.tmdb.org/t/p/w500/tYfijzolzgoMOtegh1Y7j2Enorg.jpg", "backdrop": "https://image.tmdb.org/t/p/original/2Pd6V8UBVxcpT2dXR1tAOPjt3oV.jpg", "description": "The X-Men send Wolverine to the past in a desperate effort to change history and prevent an event that results in doom for both humans and mutants.", "duration": 132, "director": "Bryan Singer", "cast": ["Patrick Stewart", "Ian McKellen", "Hugh Jackman"], "popularity": 86, "media_type": "movie"},
    {"id": 94, "title": "Wonder Woman", "year": 2017, "genres": ["Action", "Adventure", "Fantasy"], "rating": 7.4, "poster": "https://image.tmdb.org/t/p/w500/gfJGlDaHuWimTnvzBLYt7IPMJky.jpg", "backdrop": "https://image.tmdb.org/t/p/original/6ebLPnmd53rYYrKOBMbzLvdOVnL.jpg", "description": "When a pilot crashes and tells of conflict in the outside world, Diana, an Amazonian warrior in training, leaves home to fight a war, discovering her full powers and true destiny.", "duration": 141, "director": "Patty Jenkins", "cast": ["Gal Gadot", "Chris Pine", "Robin Wright"], "popularity": 87, "media_type": "movie"},
    {"id": 95, "title": "Aquaman", "year": 2018, "genres": ["Action", "Adventure", "Fantasy"], "rating": 6.9, "poster": "https://image.tmdb.org/t/p/w500/xLPffWMhMj1l50ND3KchMjYoKmE.jpg", "backdrop": "https://image.tmdb.org/t/p/original/9Qfqp4O0dGh3r1gKT3VjdIB9dUQ.jpg", "description": "Arthur Curry, the human-born heir to the underwater kingdom of Atlantis, goes on a quest to prevent a war between the worlds of ocean and land.", "duration": 143, "director": "James Wan", "cast": ["Jason Momoa", "Amber Heard", "Willem Dafoe"], "popularity": 85, "media_type": "movie"},
    {"id": 96, "title": "Shazam!", "year": 2019, "genres": ["Action", "Adventure", "Comedy", "Fantasy"], "rating": 7.0, "poster": "https://image.tmdb.org/t/p/w500/xnopI5Xtky18MPhK40cZAGAOVeV.jpg", "backdrop": "https://image.tmdb.org/t/p/original/c5O3A0kb7YJLVqE7MkpfKbLxAVg.jpg", "description": "A newly fostered young boy in search of his mother instead finds unexpected super powers and soon gains a powerful enemy.", "duration": 132, "director": "David F. Sandberg", "cast": ["Zachary Levi", "Mark Strong", "Asher Angel"], "popularity": 84, "media_type": "movie"},
    {"id": 97, "title": "Suicide Squad", "year": 2016, "genres": ["Action", "Adventure", "Comedy", "Fantasy"], "rating": 5.9, "poster": "https://image.tmdb.org/t/p/w500/rbmaga6LmBPpKsQYFSrWVqLfA7e.jpg", "backdrop": "https://image.tmdb.org/t/p/original/ndlQ2Cuc3cjTL7lTynw6I4boP4S.jpg", "description": "A secret government agency recruits some of the most dangerous incarcerated super-villains to form a defensive task force.", "duration": 123, "director": "David Ayer", "cast": ["Will Smith", "Jared Leto", "Margot Robbie"], "popularity": 83, "media_type": "movie"},
    {"id": 98, "title": "The Suicide Squad", "year": 2021, "genres": ["Action", "Adventure", "Comedy", "Fantasy"], "rating": 7.2, "poster": "https://image.tmdb.org/t/p/w500/kb4s0ML0iVZlG6wAKbbs9NAm6X.jpg", "backdrop": "https://image.tmdb.org/t/p/original/jlGmlFOcfo8n5tURmhC7YVd4Ybz.jpg", "description": "Supervillains Harley Quinn, Bloodsport, Peacemaker and a collection of nutty cons at Belle Reve prison join the super-secret, super-shady Task Force X as they are dropped off at the remote, enemy-infused island of Corto Maltese.", "duration": 132, "director": "James Gunn", "cast": ["Margot Robbie", "Idris Elba", "John Cena"], "popularity": 86, "media_type": "movie"},
    {"id": 99, "title": "Venom", "year": 2018, "genres": ["Action", "Horror", "Sci-Fi"], "rating": 6.7, "poster": "https://image.tmdb.org/t/p/w500/2uNW4WbgBXL25BAbXGLnLqX71Sw.jpg", "backdrop": "https://image.tmdb.org/t/p/original/VuukZLgaCrho2Ar8Scl9HtV3yD.jpg", "description": "A failed reporter is bonded to an alien entity, one of many combatants sent to conquer worlds. Now he must release his newfound power against the forces of evil.", "duration": 112, "director": "Ruben Fleischer", "cast": ["Tom Hardy", "Michelle Williams", "Riz Ahmed"], "popularity": 85, "media_type": "movie"},
    {"id": 100, "title": "Joker: Folie à Deux", "year": 2024, "genres": ["Crime", "Drama", "Musical", "Thriller"], "rating": 5.8, "poster": "https://image.tmdb.org/t/p/w500/if8QiqCI7WAGImKcJCfzp6VTyKA.jpg", "backdrop": "https://image.tmdb.org/t/p/original/uGmYqxh8flqkudioyFtD7IJSHxK.jpg", "description": "Arthur Fleck is institutionalized at Arkham awaiting trial for his crimes as Joker. While struggling with his dual identity, Arthur not only stumbles upon true love, but also finds the music that's always been inside him.", "duration": 138, "director": "Todd Phillips", "cast": ["Joaquin Phoenix", "Lady Gaga", "Brendan Gleeson"], "popularity": 82, "media_type": "movie"}
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
    # Generate random profile for unknown users
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
        
        # Genre matching
        matched = item_genres & preferred
        if matched:
            score += len(matched) * 0.3
            reasons.append(f"Matches your favorite genres: {', '.join(matched)}")
        
        # Penalty for disliked
        if item_genres & disliked:
            score -= 0.2
        
        # Rating bonus
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


# ============================================
# HELPER FUNCTIONS
# ============================================

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


# Pydantic models
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


# API Routes
@app.get("/")
async def root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "static", "index.html"))


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
    import time
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
