# AWS Architecture Generator

A full-stack application that generates custom AWS architectures based on user requirements, complete with Infrastructure as Code templates and cost estimates.

## Features

- Interactive questionnaire for requirements gathering
- AWS service selection and recommendations
- Real-time cost estimation with breakdown
- Security recommendations and best practices
- Terraform and CloudFormation template generation
- Interactive architecture diagram visualization
- Responsive web interface

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 with TypeScript
- **UI**: Chakra UI
- **Containerization**: Docker & Docker Compose

## Prerequisites

### Install Docker and Docker Compose

- **Windows/macOS**: [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

Verify installation:
```bash
docker --version
docker-compose --version
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ersanjeev007/AWS-Architecture-Generator.git
   cd AWS-Architecture-Generator
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## Development Setup (Optional)

If you prefer to run without Docker:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Project Structure

```
aws-architecture-generator/
├── backend/           # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          # React frontend
│   ├── src/
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Usage

1. Open [http://localhost:3000](http://localhost:3000)
2. Complete the questionnaire about your requirements
3. Review the generated AWS architecture
4. Download Terraform or CloudFormation templates
5. Deploy using your preferred Infrastructure as Code tool

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
