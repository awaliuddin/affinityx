"""
Code generation templates for the Implementer Agent.
"""


def get_backend_main_template(spec: str) -> str:
    """Get FastAPI main application template"""
    return '''"""
Generated FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from database import init_db

app = FastAPI(title="Generated App", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "API is running", "status": "ok"}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}
'''


def get_backend_models_template(spec: str) -> str:
    """Get Pydantic models template"""
    return '''"""
Data models for the application.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: str
    user_id: str
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
'''


def get_backend_routes_template(spec: str) -> str:
    """Get API routes template"""
    return '''"""
API routes for the application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from models import User, UserCreate, Item, ItemCreate, ItemUpdate, Token
from database import get_db
from auth import authenticate_user, create_access_token, get_current_user
import uuid
from datetime import datetime

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Auth endpoints
@router.post("/api/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # In a real app, hash the password and save to DB
    return {
        "id": str(uuid.uuid4()),
        "email": user.email,
        "created_at": datetime.utcnow(),
    }


@router.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login user"""
    # In a real app, verify credentials
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Item endpoints (todo/generic CRUD)
@router.get("/api/items", response_model=List[Item])
async def get_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all items for current user"""
    # In a real app, query DB
    return []


@router.post("/api/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new item"""
    now = datetime.utcnow()
    return {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "title": item.title,
        "description": item.description,
        "completed": False,
        "created_at": now,
        "updated_at": now,
    }


@router.patch("/api/items/{item_id}", response_model=Item)
async def update_item(
    item_id: str,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item"""
    # In a real app, query and update DB
    now = datetime.utcnow()
    return {
        "id": item_id,
        "user_id": current_user["id"],
        "title": item_update.title or "Updated Item",
        "description": item_update.description,
        "completed": item_update.completed or False,
        "created_at": datetime.utcnow(),
        "updated_at": now,
    }


@router.delete("/api/items/{item_id}")
async def delete_item(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an item"""
    # In a real app, delete from DB
    return {"success": True}
'''


def get_backend_database_template() -> str:
    """Get database connection template"""
    return '''"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create tables"""
    Base.metadata.create_all(bind=engine)
'''


def get_backend_requirements() -> str:
    """Get Python requirements"""
    return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
'''


def get_auth_template() -> str:
    """Get authentication module template"""
    return '''"""
Authentication utilities.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # In a real app, query user from DB
    return {"id": "user-123", "email": username}


def authenticate_user(email: str, password: str):
    """Authenticate a user"""
    # In a real app, query DB and verify password
    return {"id": "user-123", "email": email}
'''


def get_frontend_package_json() -> str:
    """Get package.json for frontend"""
    return '''{
  "name": "generated-app",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
'''


def get_frontend_app_template(spec: str) -> str:
    """Get React App template"""
    return '''import React, { useState, useEffect } from 'react';
import './App.css';

interface Item {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
}

function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [newItemTitle, setNewItemTitle] = useState('');
  const [newItemDescription, setNewItemDescription] = useState('');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  const API_URL = 'http://localhost:8000';

  useEffect(() => {
    if (token) {
      fetchItems();
    }
  }, [token]);

  const fetchItems = async () => {
    try {
      const response = await fetch(`${API_URL}/api/items`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setItems(data);
      }
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', 'user@example.com');
    formData.append('password', 'password');

    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        body: formData,
      });
      if (response.ok) {
        const data = await response.json();
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleCreateItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemTitle.trim() || !token) return;

    try {
      const response = await fetch(`${API_URL}/api/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: newItemTitle,
          description: newItemDescription,
        }),
      });

      if (response.ok) {
        const newItem = await response.json();
        setItems([...items, newItem]);
        setNewItemTitle('');
        setNewItemDescription('');
      }
    } catch (error) {
      console.error('Failed to create item:', error);
    }
  };

  const handleToggleComplete = async (id: string, completed: boolean) => {
    try {
      const response = await fetch(`${API_URL}/api/items/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ completed: !completed }),
      });

      if (response.ok) {
        const updatedItem = await response.json();
        setItems(items.map(item => item.id === id ? updatedItem : item));
      }
    } catch (error) {
      console.error('Failed to update item:', error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/api/items/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setItems(items.filter(item => item.id !== id));
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  if (!token) {
    return (
      <div className="app">
        <div className="login-container">
          <h1>Welcome</h1>
          <p>Please login to continue</p>
          <form onSubmit={handleLogin}>
            <button type="submit">Login</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>My App</h1>
        <button onClick={() => { setToken(null); localStorage.removeItem('token'); }}>
          Logout
        </button>
      </header>

      <main>
        <form onSubmit={handleCreateItem} className="create-form">
          <input
            type="text"
            placeholder="Title"
            value={newItemTitle}
            onChange={(e) => setNewItemTitle(e.target.value)}
          />
          <input
            type="text"
            placeholder="Description (optional)"
            value={newItemDescription}
            onChange={(e) => setNewItemDescription(e.target.value)}
          />
          <button type="submit">Add Item</button>
        </form>

        <div className="items-list">
          {items.length === 0 ? (
            <p className="empty-state">No items yet. Create one above!</p>
          ) : (
            items.map(item => (
              <div key={item.id} className="item">
                <input
                  type="checkbox"
                  checked={item.completed}
                  onChange={() => handleToggleComplete(item.id, item.completed)}
                />
                <div className="item-content">
                  <h3 className={item.completed ? 'completed' : ''}>{item.title}</h3>
                  {item.description && <p>{item.description}</p>}
                </div>
                <button onClick={() => handleDelete(item.id)} className="delete-btn">
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
'''


def get_frontend_main_template() -> str:
    """Get main.tsx template"""
    return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''


def get_vite_config() -> str:
    """Get vite.config.ts"""
    return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
})
'''


def get_index_html() -> str:
    """Get index.html"""
    return '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Generated App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''


def get_tsconfig() -> str:
    """Get tsconfig.json"""
    return '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'''
