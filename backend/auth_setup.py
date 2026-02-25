from google_auth_oauthlib.flow import InstalledAppFlow
import json

# Scopes: Gmail read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    # Create the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )

    # This opens a browser window for login
    creds = flow.run_local_server(port=0)

    # Save credentials to token.json
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("✅ Authentication successful! token.json created.")

if __name__ == '__main__':
    main()
