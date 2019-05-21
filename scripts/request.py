from requests import Session


if __name__ == "__main__":
    s = Session()
    r = s.get('http://127.0.0.1:8080/', params={"alias": "ABC.DEF"})
    print(f"status: {r.status_code} / symbol: {r.text}")
