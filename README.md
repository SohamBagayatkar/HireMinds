# HireMinds – Setup Guide

## 🧩 Clone the Repository
```bash
git clone https://github.com/SohamBagayatkar/HireMinds.git
cd HireMinds
```

## 🧩 Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # For Windows
# source venv/bin/activate   # For macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

## 🧩 Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```



