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
            'pH': [r'pH[:\s]+([\d.]+)', r'\bpH\b[\s:]*([0-9.]+)'],
            'EC': [r'EC[:\s]+([\d.]+)', r'\bEC\b[\s:]*([0-9.]+)'],
            'N': [r'\bN\b[:\s]+([\d.]+)', r'Nitrogen[:\s]+([\d.]+)'],
            'Nitrogen': [r'Nitrogen[:\s]+([\d.]+)', r'\bN\b[:\s]+([\d.]+)'],
            'P': [r'\bP\b[:\s]+([\d.]+)', r'Phosphorus[:\s]+([\d.]+)'],
            'Phosphorus': [r'Phosphorus[:\s]+([\d.]+)', r'\bP\b[:\s]+([\d.]+)'],
            'K': [r'\bK\b[:\s]+([\d.]+)', r'Potassium[:\s]+([\d.]+)'],
            'Potassium': [r'Potassium[:\s]+([\d.]+)', r'\bK\b[:\s]+([\d.]+)'],
            'OC': [r'\bOC\b[:\s]+([\d.]+)', r'Organic\s+Carbon[:\s]+([\d.]+)'],
            'Organic Carbon': [r'Organic\s+Carbon[:\s]+([\d.]+)', r'\bOC\b[:\s]+([\d.]+)'],
            'Zn': [r'\bZn\b[:\s]+([\d.]+)', r'Zinc[:\s]+([\d.]+)'],
            'Zinc': [r'Zinc[:\s]+([\d.]+)', r'\bZn\b[:\s]+([\d.]+)'],
            'Fe': [r'\bFe\b[:\s]+([\d.]+)', r'Iron[:\s]+([\d.]+)'],
            'Iron': [r'Iron[:\s]+([\d.]+)', r'\bFe\b[:\s]+([\d.]+)'],
            'Mn': [r'\bMn\b[:\s]+([\d.]+)', r'Manganese[:\s]+([\d.]+)'],
            'Manganese': [r'Manganese[:\s]+([\d.]+)', r'\bMn\b[:\s]+([\d.]+)'],
            'B': [r'\bB\b[:\s]+([\d.]+)', r'Boron[:\s]+([\d.]+)'],
            'Boron': [r'Boron[:\s]+([\d.]+)', r'\bB\b[:\s]+([\d.]+)'],
        }
        
        for param, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    params[param] = {'value': float(match.group(1))}
                    break
        
        return params
