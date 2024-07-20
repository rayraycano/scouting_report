# Scouting Report 
Generate scouting reports based on box scores from basketball games and AI
## Setup
ensure you have an OPEN_AI_KEY set
```bash
export OPEN_AI_KEY=...
```

install pyenv and python to set the foundation for your environment
afterwards
```bash
pip install -r requirements.txt
```

install node and npm
afterwards
```bash
npm install
```


Run Server

```bash
cd server
python -m quart run --port=3001 --reload
```

Run Client
```bash
cd client
npm run start
```

Scripts are available to run to seed the "db" (the local filesystem)
