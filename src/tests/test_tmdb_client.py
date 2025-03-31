"""Tests for TMDB API client."""
import unittest
from datetime import date
from typing import Dict, List

import os
from dotenv import load_dotenv
from src.data_processing.external.tmdb.client import TMDBClient, TMDBError, TMDBRateLimitError, TMDBAuthenticationError

# Load environment variables
load_dotenv()

class TestTMDBClient(unittest.TestCase):
    """Test cases for TMDB API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = TMDBClient()
        # Known show for consistent testing
        self.test_show_name = "The Last of Us"
        self.test_show_id = 100088  # TMDB ID for "The Last of Us"
    
    def test_search_tv_show(self):
        """Test TV show search functionality."""
        results = self.client.search_tv_show(self.test_show_name)
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0, "Should find at least one result")
        
        first_result = results[0]
        self.assertTrue(hasattr(first_result, 'id'))
        self.assertTrue(hasattr(first_result, 'name'))
        self.assertTrue(hasattr(first_result, 'overview'))
        self.assertTrue(hasattr(first_result, 'first_air_date'))
        self.assertTrue(hasattr(first_result, 'genre_ids'))
        
        # Verify it found our test show
        matching_shows = [show for show in results 
                        if show.name.lower() == self.test_show_name.lower()]
        self.assertTrue(len(matching_shows) > 0, 
                       f"Should find '{self.test_show_name}' in results")
    
    def test_get_tv_show_details(self):
        """Test retrieving detailed TV show information."""
        details = self.client.get_tv_show_details(self.test_show_id)
        
        # Verify required fields
        self.assertEqual(details.id, self.test_show_id)
        self.assertEqual(details.name, self.test_show_name)
        self.assertTrue(hasattr(details, 'overview'))
        self.assertTrue(hasattr(details, 'first_air_date'))
        self.assertTrue(hasattr(details, 'genres'))
        self.assertTrue(hasattr(details, 'status'))
        self.assertTrue(hasattr(details, 'number_of_seasons'))
        
        # Verify genres structure
        self.assertIsInstance(details.genres, list)
        if details.genres:
            genre = details.genres[0]
            self.assertTrue(hasattr(genre, 'id'))
            self.assertTrue(hasattr(genre, 'name'))
    
    def test_get_genre_list(self):
        """Test retrieving TV genre list."""
        genres = self.client.get_genre_list()
        
        self.assertIsInstance(genres, list)
        self.assertTrue(len(genres) > 0, "Should return multiple genres")
        
        # Verify genre structure
        genre = genres[0]
        self.assertTrue(hasattr(genre, 'id'))
        self.assertTrue(hasattr(genre, 'name'))
        
        # Verify some known genres are present
        genre_names = {g.name for g in genres}
        expected_genres = {'Drama', 'Comedy', 'Action & Adventure'}
        self.assertTrue(expected_genres.issubset(genre_names),
                       "Common genres should be present")
    
    def test_invalid_show_id(self):
        """Test error handling for invalid show ID."""
        with self.assertRaises(TMDBError):
            self.client.get_tv_show_details(-1)
    
    def test_search_with_special_chars(self):
        """Test search with special characters is properly encoded."""
        # This shouldn't raise any errors
        results = self.client.search_tv_show("Game & Thrones")
        self.assertIsInstance(results, list)

if __name__ == '__main__':
    unittest.main()
