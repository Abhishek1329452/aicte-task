import time
import httpx

API = "http://127.0.0.1:8000/chat"

def post(msg, session=None):
    payload = {"message": msg}
    if session:
        payload["session_id"] = session
    print(f"-> Request payload: {payload}")
    try:
        with httpx.Client(timeout=10) as c:
            r = c.post(API, json=payload)
            print(f"<- Response status: {r.status_code}")
            try:
                print(f"<- Response json: {r.json()}")
            except Exception:
                print(f"<- Response text: {r.text}")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        print(f"!! Request error: {e}")
        raise


def main():
    # wait for server
    for i in range(20):
        try:
            r = post("Hello, I need help")
            break
        except Exception as e:
            time.sleep(0.5)
    else:
        print("Server did not respond")
        return

    print("Step1 ->", r)
    sid = r.get("session_id")

    r2 = post("John Doe", sid)
    print("Step2 ->", r2)

    r3 = post("45", sid)
    print("Step3 ->", r3)

if __name__ == '__main__':
    main()
