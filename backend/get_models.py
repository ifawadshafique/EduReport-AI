import urllib.request, json
with open('.env') as f:
    key = [line.split('=')[1].strip() for line in f if line.startswith('GROQ_API_KEY')][0]
    key = key.strip('"\'')
r = urllib.request.Request('https://api.groq.com/openai/v1/models', headers={'Authorization': f'Bearer {key}'})
try:
    data = json.loads(urllib.request.urlopen(r).read())
    print([m['id'] for m in data['data'] if 'llama' in m['id']])
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print(e.read().decode())
