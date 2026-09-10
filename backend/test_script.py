import urllib.request, urllib.error, json

BASE = 'http://localhost:5000/api'

def req(path, body=None, token=None, method='GET'):
    headers = {'Content-Type': 'application/json'} if body else {}
    if token: headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body else None
    
    r = urllib.request.Request(f'{BASE}{path}', data=data, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(r)
        return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()) if e.read() else {}

# 1. Register & Login
s, r = req('/auth/register', {'name': 'Teacher', 'email': 't@test.com', 'password': 'password'}, method='POST')
if s == 409: s, r = req('/auth/login', {'email': 't@test.com', 'password': 'password'}, method='POST')
tkn = r.get('access_token')

# 2. Add Student
s, r = req('/students', {'first_name': 'Test', 'last_name': 'Student'}, tkn, 'POST')
sid = r.get('id')
print(f'Student Setup: {s}')

# 3. Add Subject
s, r = req('/subjects', {'name': 'Math'}, tkn, 'POST')
subid = r.get('id')
print(f'Subject Setup: {s}')

# --- ATTENDANCE ---
s1, _ = req(f'/students/{sid}/attendance', {'date': '2023-10-01', 'status': 'present'}, tkn, 'POST')
s2, r2 = req(f'/students/{sid}/attendance', {'date': '2023-10-01', 'status': 'absent'}, tkn, 'POST') # Duplicate -> 409
s3, _ = req(f'/students/{sid}/attendance', {'date': '2023-10-02', 'status': 'late'}, tkn, 'POST')
_, att = req(f'/students/{sid}/attendance', token=tkn)
if att and len(att) >= 2:
    att0_id = att[0]['id']
    att1_id = att[1]['id']
    s4, _ = req(f'/students/{sid}/attendance/{att0_id}', {'status': 'excused'}, tkn, 'PUT')
    s5, _ = req(f'/students/{sid}/attendance/{att1_id}', token=tkn, method='DELETE')
else:
    s4, s5 = "ERR", "ERR"
print(f'Attendance: Add={s1}, Dup={s2} - msg={r2.get("error", "")}, Put={s4}, Del={s5}')

# --- ASSESSMENTS ---
s1, _ = req(f'/students/{sid}/assessments', {'name': 'Quiz1', 'max_marks': 100, 'obtained_marks': 85}, tkn, 'POST')
s2, r2 = req(f'/students/{sid}/assessments', {'name': 'Quiz2', 'max_marks': 100, 'obtained_marks': 105}, tkn, 'POST') # Over max -> 400
_, ast = req(f'/students/{sid}/assessments', token=tkn)
if ast and len(ast) >= 1:
    ast0_id = ast[0]['id']
    s3, _ = req(f'/students/{sid}/assessments/{ast0_id}', token=tkn, method='DELETE')
else:
    s3 = "ERR"
print(f'Assessments: Add={s1}, MaxViol={s2} - msg={r2.get("error", "")}, Del={s3}')

# --- TOPICS ---
s1, _ = req(f'/students/{sid}/topics', {'name': 'Algebra'}, tkn, 'POST')
_, tpc = req(f'/students/{sid}/topics', token=tkn)
if tpc and len(tpc) >= 1:
    tpc0_id = tpc[0]['id']
    s2, _ = req(f'/students/{sid}/topics/{tpc0_id}', {'status': 'completed'}, tkn, 'PUT')
    s3, _ = req(f'/students/{sid}/topics/{tpc0_id}', token=tkn, method='DELETE')
else:
    s2, s3 = "ERR", "ERR"

print(f'Topics: Add={s1}, Put={s2}, Del={s3}')
