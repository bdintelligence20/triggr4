import os
import requests
import logging
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

class WATIClient:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make a request to the WATI API."""
        url = f"{self.api_url}/api/v1/{endpoint}"
        try:
            logger.info(f"Making WATI API request: {method} {url}")
            if data:
                logger.info(f"Request data: {data}")
            if params:
                logger.info(f"Request params: {params}")
                
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params
            )
            
            logger.info(f"WATI API response status: {response.status_code}")
            
            # Log response content for debugging
            try:
                response_data = response.json()
                logger.info(f"WATI API response: {response_data}")
            except:
                logger.info(f"WATI API response (not JSON): {response.text[:200]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"WATI API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text[:500]}")
            raise
    
    # Contact Management
    def add_contact(self, phone_number: str, name: str = "", custom_params: Optional[List[Dict]] = None) -> Dict:
        """Add a contact to WATI."""
        data = {
            "name": name,
            "customParams": custom_params or []
        }
        return self._make_request("POST", f"addContact/{phone_number}", data)
    
    def update_contact_attributes(self, phone_number: str, custom_params: List[Dict]) -> Dict:
        """Update contact attributes in WATI."""
        data = {
            "customParams": custom_params
        }
        return self._make_request("POST", f"updateContactAttributes/{phone_number}", data)
    
    # Messaging
    def send_session_message(self, phone_number: str, message_text: str) -> Dict:
        """Send a session message to a contact."""
        data = {
            "messageText": message_text
        }
        return self._make_request("POST", f"sendSessionMessage/{phone_number}", data=data)
    
    def send_template_message(self, phone_number: str, template_name: str, parameters: List[Dict]) -> Dict:
        """Send a template message to a contact."""
        data = {
            "template_name": template_name,
            "broadcast_name": template_name,
            "parameters": parameters
        }
        return self._make_request("POST", "sendTemplateMessage", data=data, params={"whatsappNumber": phone_number})
    
    def send_template_messages_bulk(self, template_name: str, receivers: List[Dict]) -> Dict:
        """Send template messages to multiple contacts."""
        data = {
            "template_name": template_name,
            "broadcast_name": template_name,
            "receivers": receivers
        }
        return self._make_request("POST", "sendTemplateMessages", data=data)
    
    # Templates
    def get_message_templates(self) -> Dict:
        """Get all message templates."""
        return self._make_request("GET", "getMessageTemplates")


def get_wati_client():
    """Helper function to get a configured WATI client."""
    api_url = os.environ.get("WATI_API_URL")
    api_token = os.environ.get("WATI_API_TOKEN")
    
    if not api_url or not api_token:
        raise ValueError("WATI_API_URL and WATI_API_TOKEN environment variables must be set")
    
    return WATIClient(api_url, api_token)
