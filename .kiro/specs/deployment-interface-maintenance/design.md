# Diseño — Interfaz, Despliegue y Mantenimiento

## Arquitectura en Oracle Cloud Free Tier

```
Internet
    ↓ puerto 80/443
Nginx (reverse proxy)
    ├── /         →  Streamlit (puerto 8501)
    └── /api/     →  FastAPI + Uvicorn (puerto 8000)

VM ARM Ampere A1 (Ubuntu 22.04)
    ├── FastAPI app
    ├── Streamlit app
    └── data/
        ├── uploads/       # archivos subidos
        └── chroma_db/     # vector store local (en disco)
```

## Recursos Oracle Free Tier usados

| Recurso | Especificación | Uso en el proyecto |
|---|---|---|
| VM Compute | ARM A1 Flex, 2 OCPU, 12 GB RAM | Corre FastAPI + Streamlit + Chroma |
| Block Storage | 50 GB Always Free | SO + app + Chroma DB + uploads |
| VCN + IP pública | 1 IP pública gratuita | Acceso externo |
| Object Storage | 20 GB Always Free | Backup opcional de uploads |

> ⚠️ Desde junio 2026: el límite bajó de 4 OCPU/24 GB a 2 OCPU/12 GB. Con 2 OCPU y 12 GB RAM el proyecto corre sin problemas — FastAPI + Streamlit + Chroma consumen ~1-2 GB en total.

## Setup de la VM

### 1. Crear la instancia en OCI Console
- Shape: `VM.Standard.A1.Flex` (ARM Ampere)
- OCPUs: 2, RAM: 12 GB
- OS: Ubuntu 22.04 (imagen ARM)
- Agregar regla en Security List: abrir puertos 22, 80, 443, 8000, 8501

### 2. Instalar dependencias
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip nginx git

# Clonar el proyecto
git clone <url-del-repo>
cd challenge-alura-agente-g10

# Crear entorno virtual
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
nano .env  # agregar GEMINI_API_KEY, CHROMA_PATH, etc.
```

### 4. Correr el backend con systemd (para que arranque automático)
Crear `/etc/systemd/system/rag-api.service`:
```ini
[Unit]
Description=RAG FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/challenge-alura-agente-g10
EnvironmentFile=/home/ubuntu/challenge-alura-agente-g10/.env
ExecStart=/home/ubuntu/challenge-alura-agente-g10/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable rag-api
sudo systemctl start rag-api
```

### 5. Correr Streamlit con systemd
Crear `/etc/systemd/system/rag-ui.service`:
```ini
[Unit]
Description=RAG Streamlit UI
After=rag-api.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/challenge-alura-agente-g10
EnvironmentFile=/home/ubuntu/challenge-alura-agente-g10/.env
ExecStart=/home/ubuntu/challenge-alura-agente-g10/.venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

### 6. Configurar Nginx como reverse proxy
```nginx
server {
    listen 80;
    server_name <IP_PUBLICA>;

    # Streamlit (interfaz web)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # FastAPI (API + Swagger)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
    }
}
```

## Interfaz Streamlit (`streamlit_app.py`)

### Secciones
1. **Subir documentos** — file picker + botón de subida, muestra el resumen de indexación
2. **Chat con el agente** — input de pregunta, respuesta con citas, historial de la sesión
3. **Documentos indexados** — lista de archivos en el sistema

### Por respuesta
```
👤 ¿Cuántos días de vacaciones tengo?

🤖 Los empleados tienen 15 días hábiles de vacaciones por año.

📄 Fuentes:
  • manual_empleados.pdf — Vacaciones — Página 12

¿Útil?  👍  👎
```

### Sesión
- Historial en `st.session_state` — dura mientras la pestaña está abierta.
- No hay persistencia entre sesiones (suficiente para el challenge).

## Variables de entorno (`.env`)

```env
# Google Gemini (una sola key para LLM + embeddings)
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL_ID=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=text-embedding-004

# Vector Store
VECTOR_STORE=chroma
CHROMA_PATH=./data/chroma_db

# App
UPLOAD_PATH=./data/uploads
LOG_PATH=./data/query_log.jsonl
```

## Logging básico

Guardar un registro JSONL de cada pregunta:
```python
{
    "timestamp": "2026-07-19T21:00:00",
    "question": "¿Cuántos días de vacaciones tengo?",
    "fallback_used": false,
    "fallback_reason": null,
    "response_time_ms": 1450,
    "model": "gemini-2.5-flash",
    "feedback": null
}
```

Sirve para revisar el desempeño del agente durante la presentación.

## Pipeline de actualización de documentos

Cuando cambia un documento:
1. Subir el nuevo archivo via Streamlit o `POST /api/v1/documents/upload`
2. El `IndexingService` borra los chunks anteriores del documento
3. Genera y guarda los nuevos embeddings en Chroma
4. La base de conocimiento queda actualizada en segundos

No se necesita detección automática de cambios para el challenge.
