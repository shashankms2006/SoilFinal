import pdfplumber
import re
from typing import Dict

class MultiEngineExtractor:
    def __init__(self):
        pass
    
    def load_engines(self):
        pass
    
    def process_file(self, file_path: str) -> Dict:
        """Extract soil parameters from PDF using pdfplumber only"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return self._extract_parameters(text)
        except Exception as e:
            return {}
    
    def _extract_parameters(self, text: str) -> Dict:
        """Extract soil parameters from text"""
        params = {}
        
        patterns = {
            'pH': r'pH[:\s]+(\d+\.?\d*)',
            'EC': r'EC[:\s]+(\d+\.?\d*)',
            'Nitrogen': r'Nitrogen[:\s]+(\d+\.?\d*)',
            'Phosphorus': r'Phosphorus[:\s]+(\d+\.?\d*)',
            'Potassium': r'Potassium[:\s]+(\d+\.?\d*)',
            'Organic Carbon': r'Organic\s+Carbon[:\s]+(\d+\.?\d*)',
            'Zinc': r'Zinc[:\s]+(\d+\.?\d*)',
            'Iron': r'Iron[:\s]+(\d+\.?\d*)',
            'Manganese': r'Manganese[:\s]+(\d+\.?\d*)',
            'Boron': r'Boron[:\s]+(\d+\.?\d*)',
        }
        
        for param, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                params[param] = {'value': float(match.group(1))}
        
        return params
