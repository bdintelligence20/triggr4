import os
import json
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
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, form_data: bool = False) -> Dict:
        """Make a request to the WATI API."""
        url = f"{self.api_url}/api/v1/{endpoint}"
        try:
            logger.info(f"Making WATI API request: {method} {url}")
            if data:
                logger.info(f"Request data: {data}")
            if params:
                logger.info(f"Request params: {params}")
            
            # Use form data or JSON based on the parameter
            if form_data:
                logger.info(f"Using form data format")
                headers = self.headers.copy()
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,  # Use data parameter for form data
                    params=params
                )
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,  # Use json parameter for JSON data
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
        # Ensure message text is not empty
        if not message_text or message_text.strip() == "":
            logger.warning("Attempted to send empty message, adding placeholder text")
            message_text = "No message content available."
        
        logger.info(f"Sending session message to {phone_number}: {message_text[:50]}...")
        
        # According to the Postman collection, this should be form data, not JSON
        form_data = {
            "messageText": message_text
        }
        
        # Try with form data first (this is the format shown in the Postman collection)
        try:
            return self._make_request("POST", f"sendSessionMessage/{phone_number}", data=form_data, form_data=True)
        except Exception as e:
            logger.warning(f"Failed to send using form data format: {str(e)}")
            
            # Try alternative approaches if form data fails
            try:
                # Try with JSON format
                json_data = {
                    "messageText": message_text
                }
                return self._make_request("POST", f"sendSessionMessage/{phone_number}", data=json_data)
            except Exception as e2:
                logger.warning(f"Failed with JSON format: {str(e2)}")
                
                # Try the text message endpoint as a last resort
                try:
                    alt_data = {
                        "phone_number": phone_number,
                        "message": message_text
                    }
                    return self._make_request("POST", "sendTextMessage", data=alt_data)
                except Exception as e3:
                    logger.warning(f"All message sending attempts failed: {str(e3)}")
                    raise
    
    def send_template_message(self, phone_number: str, template_name: str, parameters: List[Dict]) -> Dict:
        """Send a template message to a contact."""
        # Validate parameters to ensure no empty values
        validated_parameters = []
        for param in parameters:
            if 'name' in param and 'value' in param:
                # Ensure value is not empty
                if not param['value'] or str(param['value']).strip() == "":
                    logger.warning(f"Empty parameter value for {param['name']}, using placeholder")
                    param['value'] = "No content available"
                validated_parameters.append(param)
            else:
                logger.warning(f"Skipping invalid parameter: {param}")
        
        logger.info(f"Sending template message '{template_name}' to {phone_number} with {len(validated_parameters)} parameters")
        
        # According to the Postman collection, template messages use JSON format
        json_data = {
            "template_name": template_name,
            "broadcast_name": template_name,
            "parameters": validated_parameters
        }
        
        # Try with the standard JSON format first
        try:
            return self._make_request("POST", "sendTemplateMessage", data=json_data, params={"whatsappNumber": phone_number})
        except Exception as e:
            logger.warning(f"Failed to send template message with standard format: {str(e)}")
            
            # Try with form data as an alternative
            try:
                # Convert parameters to a format that can be sent as form data
                form_data = {
                    "template_name": template_name,
                    "broadcast_name": template_name,
                    "parameters": json.dumps(validated_parameters)  # Convert list to JSON string
                }
                return self._make_request("POST", "sendTemplateMessage", data=form_data, form_data=True, params={"whatsappNumber": phone_number})
            except Exception as e2:
                logger.warning(f"Failed with form data format: {str(e2)}")
                
                # Try alternative JSON formats
                try:
                    alt_data = {
                        "templateName": template_name,  # Try camelCase
                        "broadcastName": template_name,
                        "parameters": validated_parameters
                    }
                    return self._make_request("POST", "sendTemplateMessage", data=alt_data, params={"whatsappNumber": phone_number})
                except Exception as e3:
                    logger.warning(f"Failed with alternative JSON format: {str(e3)}")
                    
                    # Fall back to session message as last resort
                    message_text = f"Template message ({template_name}): "
                    for param in validated_parameters:
                        if param.get('name') and param.get('value'):
                            message_text += f"{param.get('value')} "
                    
                    logger.info(f"Falling back to session message: {message_text[:50]}...")
                    return self.send_session_message(phone_number, message_text)
    
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
