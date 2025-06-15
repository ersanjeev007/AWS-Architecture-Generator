# AWS Architecture Generator

A full-stack application that generates custom AWS architectures based on user requirements, complete with Infrastructure as Code templates and cost estimates.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

### Docker Development
```bash
docker-compose up --build
```

## 📖 API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## 🏗️ Architecture

- **Backend**: FastAPI with Python 3.11
- **Frontend**: React 18 with Chakra UI
- **Architecture**: Clean Architecture with separation of concerns

## 🎯 Features

- ✅ Interactive questionnaire (10 questions)
- ✅ AWS service selection algorithm
- ✅ Cost estimation with breakdown
- ✅ Security recommendations
- ✅ Architecture diagram visualization
- ✅ Terraform template generation
- ✅ CloudFormation template generation
- ✅ Responsive design with Chakra UI

## 📁 Project Structure

```
aws-architecture-generator/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Business logic
│   │   ├── schemas/     # Pydantic models
│   │   └── services/    # Service layer
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API services
│   │   └── utils/       # Constants and helpers
│   └── package.json
└── docker-compose.yml   # Full stack deployment
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.