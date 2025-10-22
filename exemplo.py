import requests

# POST salas
url = "http://127.0.0.1:5000/meetingrooms"
data = {"name": "Sala 201"}
response = requests.post(url, json=data)
print(response.status_code)

# POST reuniões
url = "http://127.0.0.1:5000/reservations"
data = {"room_name": "Sala 201", "reservation_date": "2021-10-21",
        "start_hour": "11:00", "end_hour": "13:00"}
response = requests.post(url, json=data)
print(response.status_code)

# PUT reuniões
url = "http://127.0.0.1:5000/reservations/2"
data = {"reservation_date": "2021-10-21",
        "start_hour": "14:00", 
        "end_hour": "16:00"}
response = requests.put(url, json=data)
print(response.status_code)

# DELETE reuniões
url = "http://127.0.0.1:5000/reservations/2"  
response = requests.delete(url)

print(response.status_code)
