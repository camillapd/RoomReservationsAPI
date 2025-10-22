# API de Agendamento de Salas de Reunião

## Descrição

API para gerenciamento de salas de reunião, permitindo criar, listar, editar e deletar agendamentos.  

---

## Modelagem

- **MeetingRoom**: tabela com as salas de reunião  
- **RoomReservation**: tabela com os agendamentos, contendo:
  - `room_id` (chave estrangeira para MeetingRoom)
  - `reservation_date` (data da reunião)
  - `start_hour` (horário de início)
  - `end_hour` (horário de fim)

---

## Endpoints

### Meeting Room

| Método | Endpoint        | Descrição                 |
|--------|----------------|---------------------------|
| GET    | /meetingrooms/ | Lista todas as salas      |
| POST   | /meetingrooms/ | Adiciona uma nova sala    |

### Room Reservation

| Método | Endpoint                  | Descrição                                   |
|--------|--------------------------|-------------------------------------------|
| GET    | /reservations/           | Lista todos os agendamentos               |
| POST   | /reservations/           | Cria um novo agendamento                  |
| GET    | /reservations/<id>       | Mostra detalhes de um agendamento         |
| PUT    | /reservations/<id>       | Edita as informações de um agendamento (exceto sala) |
| DELETE | /reservations/<id>       | Deleta um agendamento                     |

---

## Exemplos de uso

### GET
```python
import requests

response = requests.get("http://127.0.0.1:5000/reservations/")
print(response.json())
```

### POST
```python
import requests

data = {
    "room_name": "Sala 301",
    "reservation_date": "2025-10-20",
    "start_hour": "13:00",
    "end_hour": "14:00"
}
response = requests.post("http://127.0.0.1:5000/reservations/", json=data)
print(response.status_code, response.json())

```

### PUT
```python
import requests

data = {
    "reservation_date": "2025-10-22",
    "start_hour": "14:00",
    "end_hour": "15:00"
}
response = requests.put("http://127.0.0.1:5000/reservations/2", json=data)
print(response.status_code, response.json())
```

### DELETE
```python
import requests

response = requests.delete("http://127.0.0.1:5000/reservations/1")
print(response.status_code)
```

## Como executar a API

1. Instalar as dependências:

```bash
pip install -r requirements.txt
```

2. Rodar a API:

```bash
python app.py
```

3. Testar os endpoints usando a biblioteca requests (opcionalmente o arquivo exemplo.py testes prontos de exemplo)

(Para fazer GET pode-se acessar a URL diretamente no navegador para exibir o arquivo JSON)

