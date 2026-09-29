"""
Post-mission SLAM Map Uploader.
Transfers the final ROS 2 map to the ONA Gateway over high-speed Wi-Fi.
"""
import requests
import logging
import os

logger = logging.getLogger(__name__)

class MapUploader:
    def __init__(self, ona_ip="192.168.4.1", port=5000):
        # Default IP for a Raspberry Pi Access Point
        self.ona_url = f"http://{ona_ip}:{port}/upload_map" #to be changed once we configure the pi in the ONA

    def upload_slam_map(self, map_yaml_path, map_pgm_path):
        if not os.path.exists(map_yaml_path) or not os.path.exists(map_pgm_path):
            logger.error("Map files not found. Ensure ROS 2 map_saver has run.")
            return False

        try:
            logger.info(f"Connecting to ONA Gateway at {self.ona_url}...")
            files = {
                'yaml': open(map_yaml_path, 'rb'),
                'pgm': open(map_pgm_path, 'rb')
            }
            
            # Send the files via HTTP POST
            response = requests.post(self.ona_url, files=files, timeout=15)
            
            if response.status_code == 200:
                logger.info("SLAM Map successfully uploaded to ONA Gateway.")
                return True
            else:
                logger.error(f"ONA Gateway rejected map upload. Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Wi-Fi Network error during map upload: {e}")
            return False