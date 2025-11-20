"""
Geocoding utilities for location and pincode resolution
Uses Nominatim for reverse geocoding
"""

from geopy.geocoders import Nominatim
from typing import Tuple, Optional
import time


class LocationResolver:
    """Resolve location names and pincodes to coordinates"""

    def __init__(self, user_agent: str = "soil-health-app"):
        self.geolocator = Nominatim(user_agent=user_agent)
        self.cache = {}

    def get_location_from_pincode(self, pincode: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """
        Get location name and coordinates from pincode
        
        Args:
            pincode: Indian postal code
            
        Returns:
            Tuple of (location_name, latitude, longitude)
        """
        if pincode in self.cache:
            return self.cache[pincode]

        try:
            # Try structured query with postal code
            location = self.geolocator.geocode(
                {"postalcode": pincode, "country": "India"},
                addressdetails=True,
                timeout=10
            )

            if location:
                result = (location.address, location.latitude, location.longitude)
                self.cache[pincode] = result
                return result

            # Fallback: plain text with India
            location = self.geolocator.geocode(f"{pincode}, India", timeout=10)
            if location:
                result = (location.address, location.latitude, location.longitude)
                self.cache[pincode] = result
                return result

            return None, None, None

        except Exception as e:
            return None, None, None

    def get_location_from_name(self, location_name: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """
        Get coordinates from location name
        
        Args:
            location_name: Village, taluk, district, or city name
            
        Returns:
            Tuple of (full_address, latitude, longitude)
        """
        if location_name in self.cache:
            return self.cache[location_name]

        try:
            location = self.geolocator.geocode(f"{location_name}, India", timeout=10)
            
            if location:
                result = (location.address, location.latitude, location.longitude)
                self.cache[location_name] = result
                return result

            return None, None, None

        except Exception as e:
            return None, None, None

    def resolve_location(self, query: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """
        Resolve location from either pincode or location name
        
        Args:
            query: Pincode or location name
            
        Returns:
            Tuple of (location_name, latitude, longitude)
        """
        # Check if query looks like a pincode (mostly digits, length 4-8)
        if query.replace(" ", "").isdigit() and 4 <= len(query.replace(" ", "")) <= 8:
            return self.get_location_from_pincode(query)
        else:
            return self.get_location_from_name(query)

    def get_district_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get district name from coordinates using reverse geocoding
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            District name or None
        """
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
            if location:
                address_parts = location.address.split(',')
                # District is usually in the address
                return location.address
            return None
        except Exception as e:
            return None

    def clear_cache(self):
        """Clear the location cache"""
        self.cache.clear()
