#!/usr/bin/env python3
"""
Test suite for Video Processing Application
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add the project to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app import app
from preprocessing import preprocess, extract_frames
from models import load_model, predict


class TestVideoProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_home_route(self):
        """Test the home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Video Processing Application', response.data)

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

    def test_preprocess_function(self):
        """Test video preprocessing function"""
        # Create a simple test video (this would normally use a real video)
        # For now, we'll test that the function handles missing files properly
        with self.assertRaises(FileNotFoundError):
            preprocess('nonexistent_video.mp4')

    def test_model_loading(self):
        """Test model loading functionality"""
        model = load_model()
        self.assertIsNotNone(model)
        self.assertIn('model_type', model)

    def test_predict_function(self):
        """Test prediction functionality"""
        model = load_model()
        # Create mock frames for testing
        mock_frames = [np.random.rand(224, 224, 3) for _ in range(5)]
        results = predict(mock_frames, model)
        
        self.assertIn('predictions', results)
        self.assertIn('summary', results)
        self.assertEqual(len(results['predictions']), 5)

    def test_upload_form_exists(self):
        """Test that upload form is accessible"""
        response = self.app.get('/')
        self.assertIn(b'Upload Video', response.data.decode())


if __name__ == '__main__':
    unittest.main()