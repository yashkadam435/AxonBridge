# How to Run AxonBridge (Windows Guide)

## 1. Start the System

Open PowerShell in the root of the project (`d:\AxonBridge Project`) and run:
```powershell
docker compose -f infrastructure/docker/docker-compose.yml up -d --build
```

## 2. Accessing the Applications

- **Frontend Dashboard (Investor Demo):** [http://localhost:3000/nlp](http://localhost:3000/nlp)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 3. Useful Commands

**Stop all services:**
```powershell
docker compose -f infrastructure/docker/docker-compose.yml down
```

**View logs:**
```powershell
docker logs -f axonbridge-web
docker logs -f axonbridge-api
```

**Clean Everything (Destructive):**
If you want to wipe all databases and start completely fresh:
```powershell
docker compose -f infrastructure/docker/docker-compose.yml down -v --rmi all
```
