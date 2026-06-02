from fastapi.testclient import TestClient
from main import app

# Create a fake browser to take to FastApI app
client = TestClient(app)

def test_idor_security_block():
  # The client logs in as Alice
  login_response = client.post("/token", data={"username": "Alice", "password": "password"})
  token = login_response.json().get("access_token")


  # The client equips Alice's token and tries to view Bob's history
  headers = {"Authorization": f"Bearer {token}"}
  hacked_response = client.get("/accounts/2/history", headers=headers)

  assert hacked_response.status_code == 403
  assert hacked_response.json().get("detail") == "Not authorized to view this account history"