import requests

base = "http://127.0.0.1:5000"

# Signup
r = requests.post(base + "/api/signup", json={
    "username": "test1",
    "email": "test1@gmail.com",
    "password": "Test@123"
})
print("Signup:", r.status_code, r.text)

# Login
r = requests.post(base + "/api/login", json={
    "email": "test1@gmail.com",
    "password": "Test@123"
})
print("Login:", r.status_code, r.text)
if r.status_code == 200:
    token = r.json().get("token")
    # Profile
    headers = {"Authorization": f"Bearer {token}"}
    r2 = requests.get(base + "/api/profile", headers=headers)
    print("Profile:", r2.status_code, r2.text)
