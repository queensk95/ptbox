# Build the React app
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install  # Install dependencies
COPY frontend/ .
RUN npm run build  # Build the React app

# Set up the Python backend
FROM python:3.9-slim AS backend
WORKDIR /app
COPY backend/ .
COPY --from=frontend-builder /frontend/build /app/frontend/build
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
