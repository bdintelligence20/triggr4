# Migration from Twilio to WATI for WhatsApp Integration

This document outlines the changes made to migrate the WhatsApp integration from Twilio to WATI.

## Overview

The migration involved:

1. Creating a WATI client module
2. Updating the WhatsApp routes to use WATI instead of Twilio
3. Updating the member verification process
4. Updating the frontend WhatsApp integration component
5. Adding WATI environment variables

## Files Changed

- `backend/wati_client.py` (new file)
- `backend/routes/whatsapp_routes.py`
- `backend/routes/member_routes.py`
- `backend/app.py`
- `frontend/src/components/integration/WhatsappIntegration.tsx`

## Environment Variables

The following environment variables need to be set in your Render service:

```
WATI_API_URL=https://live-mt-server.wati.io/429342
WATI_API_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI0ODBjYTMyZC01NDA0LTRjOGEtYmMzNi1lMTIxMTZkZTUyZGEiLCJ1bmlxdWVfbmFtZSI6Im5pY0B3ZWFyZXRyaWdnci5jb20iLCJuYW1laWQiOiJuaWNAd2VhcmV0cmlnZ3IuY29tIiwiZW1haWwiOiJuaWNAd2VhcmV0cmlnZ3IuY29tIiwiYXV0aF90aW1lIjoiMDQvMTAvMjAyNSAwODozNjoyMCIsInRlbmFudF9pZCI6IjQyOTM0MiIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.X5etiyC__q9PZcEIqVZg2wLLAAIpTiNpBO7RgWO2_q4
WATI_WHATSAPP_NUMBER=15557107684
```

## WATI Templates

The following WhatsApp templates have been configured in WATI:

1. **app_verification** - Used for sending verification codes
   - Format: `{{1}} is your verification code. For your security, do not share this code.`
   - Parameter 1: Verification code

2. **welcome_message** - Used for welcoming new members after verification
   - Format: `Welcome to the {{1}} Knowledge Hub! You can ask questions about your organization's knowledge base here.`
   - Parameter 1: Organization name

3. **knowledge_response** - Used for sending knowledge base responses outside the 24-hour window
   - Format: `Here's what I found in the {{1}} knowledge base: {{2}}`
   - Parameter 1: Organization name
   - Parameter 2: AI response

## Webhook Configuration

The WATI webhook endpoint is:

```
https://triggr4bg.onrender.com/wati-webhook
```

This needs to be configured in the WATI dashboard under Settings > API > Webhooks.

### Webhook Events to Configure

In the WATI dashboard, you should enable the following webhook events:

1. **Incoming Message** - This is the most important event, as it triggers when a user sends a message to your WhatsApp number.
2. **Message Status** (optional) - This provides delivery status updates for your outgoing messages.
3. **Contact Status** (optional) - This notifies you when a contact's status changes (e.g., when they join WhatsApp).

For each event, set the webhook URL to `https://triggr4bg.onrender.com/wati-webhook`. The system is designed to handle all these event types through the same endpoint.

## Key Changes

### 1. WATI Client

A new WATI client module was created to handle communication with the WATI API. This includes:

- Sending session messages
- Sending template messages
- Managing contacts

### 2. Verification Process

The verification process now works as follows:

1. Admin clicks "Verify WhatsApp" for a member
2. Backend generates a 6-digit verification code
3. Backend stores the code in Firestore with the member record
4. Backend sends the code via WATI template message
5. Member receives the code and sends it back via WhatsApp
6. Backend validates the code and marks the member as verified
7. Backend sends a welcome message using a template

### 3. Message Handling

Messages are now handled through the WATI webhook:

1. Member sends a message to the WhatsApp number
2. WATI forwards the message to our webhook
3. Backend processes the message and generates a response
4. Backend sends the response back via WATI

### 4. Legacy Support

The original Twilio webhook endpoint is still supported for backward compatibility. It transforms the Twilio webhook data to the WATI format and forwards it to the WATI webhook handler.

## Benefits of WATI

1. **Template Messages**: Can send messages outside the 24-hour window
2. **Simplified Verification**: Direct verification through WhatsApp
3. **Better Reliability**: Improved message delivery
4. **No Sandbox Limitations**: No need for sandbox codes or approval process

## Rollback Plan

If needed, the system can be rolled back to Twilio by:

1. Removing the WATI environment variables
2. Ensuring the Twilio environment variables are set
3. Reverting the changes to the files mentioned above

The legacy webhook support ensures that the system can still function with Twilio while the migration is in progress.
