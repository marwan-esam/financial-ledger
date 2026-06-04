from fastapi.testclient import TestClient
from main import app

# Create a fake browser to take to FastApI app
client = TestClient(app)

def test_idor_security_block():
  # The client logs in as Alice
  login_response = client.post("/token", data={"username": "Alice", "password": "password"})
  token = login_response.json().get("access_token")


  # The client equips Alice's token and tries to view the history of account with ID 1
  headers = {"Authorization": f"Bearer {token}"}
  hacked_response = client.get("/accounts/1/history", headers=headers)

  assert hacked_response.status_code == 403
  assert hacked_response.json().get("detail") == "Not authorized to view this account history"


def test_insufficient_funds_block():
  # Log in as marwan (Account ID 1, that has 2000 balance)
  login_response = client.post("/token", data={"username": "marwan", "password": "password"})
  token = login_response.json().get("access_token")
  headers = {"Authorization": f"Bearer {token}"}

  # Attempt to send 1000000 to Account ID 2
  bad_transaction = {
    "sender_id": 1,
    "receiver_id": 2,
    "amount": 1000000
  }

  response = client.post("/transactions", json=bad_transaction, headers=headers)

  print(response.status_code)

  # Test to guarantee the API rejects it with status code 400 bad request
  assert response.status_code == 400
  assert response.json().get("detail") == "Insufficient funds for this transaction"