from google.cloud import secretmanager
import hashlib

# https://console.cloud.google.com/security/secret-manager?project=project-7ed37

PROJECT_ID = "project-7ed37" #269976102200

def create_secret(secret_id):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    
    # Build the resource name of the parent project.
    parent = f"projects/{PROJECT_ID}"

    # Build a dict of settings for the secret
    secret = {'replication': {'automatic': {}}}

    # Create the secret
    response = client.create_secret(secret_id=secret_id, parent=parent, secret=secret)

    # Print the new secret name.
    print(f'Created secret: {response.name}')

def add_secret_version(secret_id, payload):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the parent secret.
    parent = f"projects/{PROJECT_ID}/secrets/{secret_id}"

    # Convert the string payload into a bytes. This step can be omitted if you
    # pass in bytes instead of a str for the payload argument.
    payload = payload.encode('UTF-8')

    # Add the secret version.
    response = client.add_secret_version(parent=parent, payload={'data': payload})

    # Print the new secret version name.
    print(f'Added secret version: {response.name}')

def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

def secret_hash(secret_value): 
  # return the sha224 hash of the secret value
  return hashlib.sha224(bytes(secret_value, "utf-8")).hexdigest()