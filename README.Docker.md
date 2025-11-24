# Docker Setup for Pinterest Clone

This project is containerized using Docker to allow running both the frontend and backend with a single command.

## Prerequisites

- Docker and Docker Compose installed on your machine.

## Quick Start

1.  **Configure Environment Variables**:
    - Ensure you have a `.env` file in `vibe-search-backend/` with your database credentials.
    - (Optional) Create a `.env.local` in `frontend/` if you need custom frontend settings.

2.  **Run the Application**:
    Run the following command in the root directory:
    ```bash
    docker compose up --build
    ```

3.  **Access the App**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000](http://localhost:8000)

## Services

-   **Frontend**: Next.js application running on port 3000.
-   **Backend**: Django application running on port 8000.

## Development

-   **Hot Reloading**: Both services are configured with volume mounts, so changes to your code will automatically trigger reloads/rebuilds.
-   **ML Models**: The backend image pre-downloads the required ML models (CLIP, YOLO, Sentence-Transformer). The first build may take a few minutes.

## Troubleshooting

-   **Database Connection**: If the backend fails to connect to the database, ensure your `.env` file in `vibe-search-backend/` has the correct `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_PORT`.
-   **Port Conflicts**: Make sure ports 3000 and 8000 are not in use by other applications.
