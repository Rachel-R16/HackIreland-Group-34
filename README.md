# HackIreland-Group-34

## Frontend Setup
To get started with the React application:

```bash
cd frontend
npm install
npm start
```

This will:
1. Install dependencies
2. Start development server at http://localhost:3000
1. Install NodeJS 23.3.0.
2. Install dependencies: npm install.
3. Run the app: npm 

## Backend Setup

First install Python 3.11+ and create a virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the Flask server:
```bash
python api.py
```

The API will be available at http://localhost:5000

Test the endpoint:
```bash
curl http://localhost:5000/api/test
```