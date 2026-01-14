from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def post(msg, session=None):
    payload = {"message": msg}
    if session:
        payload["session_id"] = session
    print("-> Request payload:", payload)
    r = client.post("/chat", json=payload)
    print("<- Status:", r.status_code)
    try:
        print("<- JSON:", r.json())
    except Exception:
        print("<- Text:", r.text)
    r.raise_for_status()
    return r.json()


def main():
    r = post("I have severe chest pain")
    sid = r.get("session_id")
    r2 = post("John Doe", sid)
    r3 = post("45", sid)
    print("Final responses:\n", r, r2, r3)

if __name__ == '__main__':
    main()
