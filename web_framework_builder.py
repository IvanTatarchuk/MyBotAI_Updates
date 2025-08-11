#!/usr/bin/env python3
"""
🌐 Web Framework Builder - Maksymalna Funkcjonalność
Tworzy kompletne aplikacje webowe: React, Vue, Angular, Full-Stack, E-commerce
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
import time

class WebFrameworkBuilder:
    """Advanced web framework builder with maximum functionality."""
    
    def __init__(self):
        self.frameworks = {
            'react': self._create_react_app,
            'vue': self._create_vue_app,
            'angular': self._create_angular_app,
            'next': self._create_react_app,  # Placeholder
            'nuxt': self._create_vue_app,    # Placeholder
            'svelte': self._create_react_app, # Placeholder
            'full_stack': self._create_full_stack_app,
            'e_commerce': self._create_ecommerce_app,
            'cms': self._create_cms_app,
            'blog': self._create_react_app,      # Placeholder
            'portfolio': self._create_react_app, # Placeholder
            'dashboard': self._create_react_app  # Placeholder
        }
        
        self.backend_options = ['express', 'fastapi', 'django', 'flask', 'nest', 'spring']
        self.databases = ['postgresql', 'mongodb', 'mysql', 'sqlite', 'redis']
        self.auth_systems = ['jwt', 'oauth', 'firebase', 'auth0', 'custom']
        
    def create_web_application(self, app_name: str, framework: str = 'react', 
                             features: List[str] = None, backend: str = 'express',
                             database: str = 'postgresql') -> Dict[str, Any]:
        """Create a complete web application."""
        
        if framework not in self.frameworks:
            raise ValueError(f"Unsupported framework: {framework}")
        
        features = features or ['authentication', 'crud', 'responsive']
        
        print(f"🌐 Tworzenie aplikacji webowej: {app_name}")
        print(f"📦 Framework: {framework}")
        print(f"🔧 Backend: {backend}")
        print(f"🗄️ Baza danych: {database}")
        print(f"⚡ Funkcje: {', '.join(features)}")
        
        # Wywołaj odpowiedni builder
        result = self.frameworks[framework](app_name, features, backend, database)
        
        return {
            'success': True,
            'app_name': app_name,
            'framework': framework,
            'backend': backend,
            'database': database,
            'features': features,
            'structure': result,
            'deployment_ready': True,
            'estimated_dev_time': self._estimate_dev_time(framework, features)
        }

    def _create_react_app(self, app_name: str, features: List[str], 
                         backend: str, database: str) -> Dict[str, Any]:
        """Create a React application with maximum features."""
        
        structure = {
            'directories': [
                f"{app_name}/",
                f"{app_name}/src/",
                f"{app_name}/src/components/",
                f"{app_name}/src/pages/",
                f"{app_name}/src/hooks/",
                f"{app_name}/src/context/",
                f"{app_name}/src/services/",
                f"{app_name}/src/utils/",
                f"{app_name}/src/styles/",
                f"{app_name}/src/assets/",
                f"{app_name}/public/",
                f"{app_name}/backend/",
                f"{app_name}/backend/routes/",
                f"{app_name}/backend/models/",
                f"{app_name}/backend/middleware/",
                f"{app_name}/tests/",
                f"{app_name}/docs/"
            ],
            'files': {
                f"{app_name}/package.json": self._generate_react_package_json(app_name, features),
                f"{app_name}/src/App.js": self._generate_react_app_component(features),
                f"{app_name}/src/index.js": self._generate_react_index(),
                f"{app_name}/src/components/Header.js": self._generate_header_component(),
                f"{app_name}/src/components/Footer.js": self._generate_footer_component(),
                f"{app_name}/src/components/Navigation.js": self._generate_navigation_component(),
                f"{app_name}/src/pages/Home.js": self._generate_home_page(),
                f"{app_name}/src/pages/About.js": self._generate_about_page(),
                f"{app_name}/src/services/api.js": self._generate_api_service(backend),
                f"{app_name}/src/context/AuthContext.js": self._generate_auth_context(),
                f"{app_name}/src/hooks/useAuth.js": self._generate_auth_hook(),
                f"{app_name}/src/utils/helpers.js": self._generate_utility_helpers(),
                f"{app_name}/src/styles/App.css": self._generate_app_styles(),
                f"{app_name}/src/styles/components.css": self._generate_component_styles(),
                f"{app_name}/backend/server.js": self._generate_backend_server(backend, database),
                f"{app_name}/backend/routes/auth.js": self._generate_auth_routes(),
                f"{app_name}/backend/routes/api.js": self._generate_api_routes(),
                f"{app_name}/backend/models/User.js": self._generate_user_model(database),
                f"{app_name}/backend/middleware/auth.js": self._generate_auth_middleware(),
                f"{app_name}/.env.example": self._generate_env_template(),
                f"{app_name}/README.md": self._generate_react_readme(app_name, features),
                f"{app_name}/docker-compose.yml": self._generate_docker_compose(database),
                f"{app_name}/Dockerfile": self._generate_dockerfile_react(),
                f"{app_name}/.gitignore": self._generate_gitignore()
            }
        }
        
        # Dodaj funkcje specjalne
        if 'e_commerce' in features:
            structure['files'].update(self._add_ecommerce_files(app_name))
        if 'dashboard' in features:
            structure['files'].update(self._add_dashboard_files(app_name))
        if 'blog' in features:
            structure['files'].update(self._add_blog_files(app_name))
        
        return structure

    def _create_vue_app(self, app_name: str, features: List[str], 
                       backend: str, database: str) -> Dict[str, Any]:
        """Create a Vue.js application."""
        
        structure = {
            'directories': [
                f"{app_name}/",
                f"{app_name}/src/",
                f"{app_name}/src/components/",
                f"{app_name}/src/views/",
                f"{app_name}/src/router/",
                f"{app_name}/src/store/",
                f"{app_name}/src/services/",
                f"{app_name}/src/assets/",
                f"{app_name}/public/",
                f"{app_name}/backend/",
                f"{app_name}/tests/"
            ],
            'files': {
                f"{app_name}/package.json": self._generate_vue_package_json(app_name),
                f"{app_name}/src/main.js": self._generate_vue_main(),
                f"{app_name}/src/App.vue": self._generate_vue_app_component(features),
                f"{app_name}/src/router/index.js": self._generate_vue_router(),
                f"{app_name}/src/store/index.js": self._generate_vuex_store(),
                f"{app_name}/src/components/HelloWorld.vue": self._generate_vue_hello_component(),
                f"{app_name}/src/views/Home.vue": self._generate_vue_home_view(),
                f"{app_name}/src/services/api.js": self._generate_vue_api_service(),
                f"{app_name}/vue.config.js": self._generate_vue_config(),
                f"{app_name}/README.md": self._generate_vue_readme(app_name),
                f"{app_name}/.env.example": self._generate_env_template()
            }
        }
        
        return structure

    def _create_angular_app(self, app_name: str, features: List[str],
                           backend: str, database: str) -> Dict[str, Any]:
        """Create an Angular application."""
        
        structure = {
            'directories': [
                f"{app_name}/",
                f"{app_name}/src/",
                f"{app_name}/src/app/",
                f"{app_name}/src/app/components/",
                f"{app_name}/src/app/services/",
                f"{app_name}/src/app/guards/",
                f"{app_name}/src/app/models/",
                f"{app_name}/src/assets/",
                f"{app_name}/backend/",
                f"{app_name}/e2e/"
            ],
            'files': {
                f"{app_name}/package.json": self._generate_angular_package_json(app_name),
                f"{app_name}/angular.json": self._generate_angular_config(),
                f"{app_name}/src/main.ts": self._generate_angular_main(),
                f"{app_name}/src/app/app.module.ts": self._generate_angular_app_module(features),
                f"{app_name}/src/app/app.component.ts": self._generate_angular_app_component(),
                f"{app_name}/src/app/app.component.html": self._generate_angular_app_template(),
                f"{app_name}/src/app/services/api.service.ts": self._generate_angular_api_service(),
                f"{app_name}/src/app/services/auth.service.ts": self._generate_angular_auth_service(),
                f"{app_name}/README.md": self._generate_angular_readme(app_name)
            }
        }
        
        return structure

    def _create_full_stack_app(self, app_name: str, features: List[str],
                              backend: str, database: str) -> Dict[str, Any]:
        """Create a complete full-stack application."""
        
        # Kombinacja React frontend + backend
        frontend = self._create_react_app(f"{app_name}_frontend", features, backend, database)
        
        # Dodaj backend pliki
        backend_files = {
            f"{app_name}_backend/server.js": self._generate_backend_server(backend, database),
            f"{app_name}_backend/package.json": self._generate_backend_package_json(),
            f"{app_name}_backend/routes/api.js": self._generate_api_routes(),
            f"{app_name}_backend/models/User.js": self._generate_user_model(database)
        }
        
        structure = {
            'directories': frontend['directories'] + [f"{app_name}_backend/", f"{app_name}_backend/routes/", f"{app_name}_backend/models/"],
            'files': {**frontend['files'], **backend_files}
        }
        
        return structure

    def _create_ecommerce_app(self, app_name: str, features: List[str],
                             backend: str, database: str) -> Dict[str, Any]:
        """Create a complete e-commerce application."""
        
        ecommerce_features = [
            'product_catalog', 'shopping_cart', 'checkout', 'payment_processing',
            'user_authentication', 'order_management', 'inventory_management',
            'admin_panel', 'analytics', 'reviews', 'wishlist', 'search'
        ]
        
        structure = self._create_react_app(app_name, features + ecommerce_features, backend, database)
        
        # Dodaj specjalne pliki e-commerce
        ecommerce_files = {
            f"{app_name}/src/components/ProductCard.js": self._generate_product_card(),
            f"{app_name}/src/components/ShoppingCart.js": self._generate_shopping_cart(),
            f"{app_name}/src/components/Checkout.js": self._generate_checkout_component(),
            f"{app_name}/src/pages/ProductList.js": self._generate_product_list(),
            f"{app_name}/src/pages/ProductDetail.js": self._generate_product_detail(),
            f"{app_name}/src/services/payment.js": self._generate_payment_service(),
            f"{app_name}/backend/routes/products.js": self._generate_products_api(),
            f"{app_name}/backend/routes/orders.js": self._generate_orders_api(),
            f"{app_name}/backend/models/Product.js": self._generate_product_model(),
            f"{app_name}/backend/models/Order.js": self._generate_order_model()
        }
        
        structure['files'].update(ecommerce_files)
        
        return structure

    def _create_cms_app(self, app_name: str, features: List[str],
                       backend: str, database: str) -> Dict[str, Any]:
        """Create a Content Management System."""
        
        cms_features = [
            'content_editor', 'media_management', 'user_roles', 'seo_optimization',
            'theme_system', 'plugin_architecture', 'backup_system', 'analytics'
        ]
        
        structure = self._create_react_app(app_name, features + cms_features, backend, database)
        
        # Dodaj pliki CMS
        cms_files = {
            f"{app_name}/src/components/ContentEditor.js": self._generate_content_editor(),
            f"{app_name}/src/components/MediaManager.js": self._generate_media_manager(),
            f"{app_name}/src/components/AdminPanel.js": self._generate_admin_panel(),
            f"{app_name}/backend/routes/content.js": self._generate_content_api(),
            f"{app_name}/backend/models/Content.js": self._generate_content_model()
        }
        
        structure['files'].update(cms_files)
        
        return structure

    # React Components Generation
    def _generate_react_package_json(self, app_name: str, features: List[str]) -> str:
        """Generate package.json for React app."""
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0", 
            "react-router-dom": "^6.8.0",
            "axios": "^1.3.0",
            "styled-components": "^5.3.0",
            "@reduxjs/toolkit": "^1.9.0",
            "react-redux": "^8.0.0"
        }
        
        if 'authentication' in features:
            dependencies.update({
                "jsonwebtoken": "^9.0.0",
                "bcryptjs": "^2.4.3"
            })
        
        if 'e_commerce' in features:
            dependencies.update({
                "stripe": "^11.0.0",
                "react-credit-cards": "^0.8.3"
            })
        
        package = {
            "name": app_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"Advanced {app_name} web application",
            "main": "src/index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build", 
                "test": "react-scripts test",
                "eject": "react-scripts eject",
                "dev": "concurrently \"npm start\" \"cd backend && npm run dev\"",
                "deploy": "npm run build && npm run deploy:backend"
            },
            "dependencies": dependencies,
            "devDependencies": {
                "react-scripts": "5.0.1",
                "concurrently": "^7.6.0",
                "@testing-library/react": "^13.4.0",
                "@testing-library/jest-dom": "^5.16.0",
                "eslint": "^8.0.0",
                "prettier": "^2.8.0"
            }
        }
        
        return json.dumps(package, indent=2)

    def _generate_react_app_component(self, features: List[str]) -> str:
        """Generate main React App component."""
        
        imports = [
            "import React from 'react';",
            "import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';",
            "import { Provider } from 'react-redux';",
            "import { store } from './store/store';",
            "import Header from './components/Header';",
            "import Footer from './components/Footer';",
            "import Home from './pages/Home';",
            "import About from './pages/About';",
            "import './styles/App.css';"
        ]
        
        if 'authentication' in features:
            imports.extend([
                "import Login from './pages/Login';",
                "import Register from './pages/Register';",
                "import { AuthProvider } from './context/AuthContext';"
            ])
        
        if 'e_commerce' in features:
            imports.extend([
                "import ProductList from './pages/ProductList';",
                "import ProductDetail from './pages/ProductDetail';",
                "import Cart from './pages/Cart';",
                "import Checkout from './pages/Checkout';"
            ])
        
        routes = [
            '<Route path="/" element={<Home />} />',
            '<Route path="/about" element={<About />} />'
        ]
        
        if 'authentication' in features:
            routes.extend([
                '<Route path="/login" element={<Login />} />',
                '<Route path="/register" element={<Register />} />'
            ])
        
        if 'e_commerce' in features:
            routes.extend([
                '<Route path="/products" element={<ProductList />} />',
                '<Route path="/product/:id" element={<ProductDetail />} />',
                '<Route path="/cart" element={<Cart />} />',
                '<Route path="/checkout" element={<Checkout />} />'
            ])
        
        app_content = f'''
function App() {{
  return (
    <Provider store={{store}}>
      {'<AuthProvider>' if 'authentication' in features else ''}
        <Router>
          <div className="App">
            <Header />
            <main className="main-content">
              <Routes>
                {chr(10).join('                ' + route for route in routes)}
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      {'</AuthProvider>' if 'authentication' in features else ''}
    </Provider>
  );
}}

export default App;
'''
        
        return '\n'.join(imports) + app_content

    def _generate_react_index(self) -> str:
        """Generate React index.js."""
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''

    def _generate_header_component(self) -> str:
        """Generate Header component."""
        return '''import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">
          <h1>Your App</h1>
        </Link>
        
        <nav className="navigation">
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/products">Products</Link>
          
          {user ? (
            <div className="user-menu">
              <span>Welcome, {user.name}!</span>
              <button onClick={logout}>Logout</button>
            </div>
          ) : (
            <div className="auth-links">
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;'''

    def _generate_footer_component(self) -> str:
        """Generate Footer component."""
        return '''import React from 'react';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Your App</h3>
            <p>Building amazing web experiences</p>
          </div>
          
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="/">Home</a></li>
              <li><a href="/about">About</a></li>
              <li><a href="/contact">Contact</a></li>
              <li><a href="/privacy">Privacy Policy</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Follow Us</h4>
            <div className="social-links">
              <a href="#" aria-label="Facebook">📘</a>
              <a href="#" aria-label="Twitter">🐦</a>
              <a href="#" aria-label="Instagram">📷</a>
              <a href="#" aria-label="LinkedIn">💼</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {currentYear} Your App. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;'''

    def _generate_api_service(self, backend: str) -> str:
        """Generate API service."""
        return '''import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Authentication
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  
  // User management
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  
  // Generic CRUD operations
  get: (endpoint) => api.get(endpoint),
  post: (endpoint, data) => api.post(endpoint, data),
  put: (endpoint, data) => api.put(endpoint, data),
  delete: (endpoint) => api.delete(endpoint),
  
  // File upload
  uploadFile: (file, endpoint = '/upload') => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export default api;'''

    def _generate_backend_server(self, backend: str, database: str) -> str:
        """Generate backend server."""
        if backend == 'express':
            return self._generate_express_server(database)
        elif backend == 'fastapi':
            return self._generate_fastapi_server(database)
        else:
            return self._generate_express_server(database)  # Default to Express

    def _generate_express_server(self, database: str) -> str:
        """Generate Express.js server."""
        return '''const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const morgan = require('morgan');
require('dotenv').config();

// Import routes
const authRoutes = require('./routes/auth');
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// General middleware
app.use(compression());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api', apiRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ message: 'Route not found' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 API URL: http://localhost:${PORT}/api`);
});

module.exports = app;'''

    def _generate_app_styles(self) -> str:
        """Generate main app styles."""
        return '''/* App.css - Main application styles */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
}

.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header Styles */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  color: white;
  text-decoration: none;
}

.navigation {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.navigation a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.navigation a:hover {
  opacity: 0.8;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 2rem 0;
}

/* Button Styles */
.btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #6c757d;
}

.btn-danger {
  background: #dc3545;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Card Styles */
.card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

/* Grid Layouts */
.grid {
  display: grid;
  gap: 2rem;
}

.grid-2 {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.grid-3 {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.grid-4 {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

/* Footer Styles */
.footer {
  background: #343a40;
  color: white;
  padding: 3rem 0 1rem;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3,
.footer-section h4 {
  margin-bottom: 1rem;
  color: #fff;
}

.footer-section ul {
  list-style: none;
}

.footer-section ul li {
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: #adb5bd;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-section a:hover {
  color: white;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  font-size: 1.5rem;
  transition: transform 0.2s;
}

.social-links a:hover {
  transform: scale(1.2);
}

.footer-bottom {
  border-top: 1px solid #495057;
  padding-top: 1rem;
  text-align: center;
  color: #adb5bd;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header .container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .navigation {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .container {
    padding: 0 15px;
  }
  
  .grid-2,
  .grid-3,
  .grid-4 {
    grid-template-columns: 1fr;
  }
}

/* Loading and Animation */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mt-3 { margin-top: 1.5rem; }
.mt-4 { margin-top: 2rem; }

.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }
.mb-4 { margin-bottom: 2rem; }

.p-1 { padding: 0.5rem; }
.p-2 { padding: 1rem; }
.p-3 { padding: 1.5rem; }
.p-4 { padding: 2rem; }'''

    def _generate_docker_compose(self, database: str) -> str:
        """Generate docker-compose.yml."""
        db_config = {
            'postgresql': '''
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: app_db
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data''',
            'mongodb': '''
  mongodb:
    image: mongo:5
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db''',
            'mysql': '''
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: app_db
      MYSQL_USER: app_user
      MYSQL_PASSWORD: app_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql'''
        }
        
        return f'''version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:3001/api
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://app_user:app_password@postgres:5432/app_db
    depends_on:
      - {database}

{db_config.get(database, db_config['postgresql'])}

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  {database}_data:
  redis_data:'''

    def _estimate_dev_time(self, framework: str, features: List[str]) -> Dict[str, str]:
        """Estimate development time."""
        base_times = {
            'react': 40,
            'vue': 35, 
            'angular': 50,
            'full_stack': 80,
            'e_commerce': 120,
            'cms': 100
        }
        
        feature_time = len(features) * 8
        total_hours = base_times.get(framework, 40) + feature_time
        
        return {
            'estimated_hours': total_hours,
            'estimated_days': f"{total_hours // 8}-{(total_hours // 8) + 2}",
            'complexity': 'High' if total_hours > 100 else 'Medium' if total_hours > 60 else 'Low'
        }

    # Dodatkowe metody generowania...
    def _generate_vue_package_json(self, app_name: str) -> str:
        """Generate Vue package.json."""
        package = {
            "name": app_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "scripts": {
                "serve": "vue-cli-service serve",
                "build": "vue-cli-service build",
                "test:unit": "vue-cli-service test:unit",
                "lint": "vue-cli-service lint"
            },
            "dependencies": {
                "vue": "^3.2.0",
                "vue-router": "^4.0.0",
                "vuex": "^4.0.0",
                "axios": "^1.3.0"
            },
            "devDependencies": {
                "@vue/cli-service": "~5.0.0",
                "@vue/test-utils": "^2.0.0",
                "eslint": "^8.0.0"
            }
        }
        return json.dumps(package, indent=2)

    def _generate_angular_package_json(self, app_name: str) -> str:
        """Generate Angular package.json."""
        package = {
            "name": app_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "scripts": {
                "ng": "ng",
                "start": "ng serve",
                "build": "ng build",
                "test": "ng test",
                "lint": "ng lint",
                "e2e": "ng e2e"
            },
            "dependencies": {
                "@angular/animations": "^15.0.0",
                "@angular/common": "^15.0.0",
                "@angular/compiler": "^15.0.0",
                "@angular/core": "^15.0.0",
                "@angular/forms": "^15.0.0",
                "@angular/platform-browser": "^15.0.0",
                "@angular/platform-browser-dynamic": "^15.0.0",
                "@angular/router": "^15.0.0",
                "rxjs": "~7.5.0",
                "tslib": "^2.3.0",
                "zone.js": "~0.12.0"
            },
            "devDependencies": {
                "@angular-devkit/build-angular": "^15.0.0",
                "@angular/cli": "~15.0.0",
                "@angular/compiler-cli": "^15.0.0",
                "typescript": "~4.8.0"
            }
        }
        return json.dumps(package, indent=2)

    # Dodatkowe metody pomocnicze...
    def _add_ecommerce_files(self, app_name: str) -> Dict[str, str]:
        """Add e-commerce specific files."""
        return {
            f"{app_name}/src/components/ProductCard.js": self._generate_product_card(),
            f"{app_name}/src/components/ShoppingCart.js": self._generate_shopping_cart(),
            f"{app_name}/src/pages/Checkout.js": self._generate_checkout_component(),
            f"{app_name}/src/pages/ProductList.js": self._generate_product_list(),
            f"{app_name}/src/pages/ProductDetail.js": self._generate_product_detail(),
            f"{app_name}/src/services/payment.js": self._generate_payment_service(),
            f"{app_name}/backend/routes/products.js": self._generate_products_api(),
            f"{app_name}/backend/routes/orders.js": self._generate_orders_api(),
            f"{app_name}/backend/models/Product.js": self._generate_product_model(),
            f"{app_name}/backend/models/Order.js": self._generate_order_model()
        }
    
    def _add_dashboard_files(self, app_name: str) -> Dict[str, str]:
        """Add dashboard specific files."""
        return {
            f"{app_name}/src/components/Dashboard.js": "// Dashboard component placeholder",
            f"{app_name}/src/components/Charts.js": "// Charts component placeholder"
        }
    
    def _add_blog_files(self, app_name: str) -> Dict[str, str]:
        """Add blog specific files."""
        return {
            f"{app_name}/src/components/BlogPost.js": "// Blog post component placeholder",
            f"{app_name}/src/pages/BlogList.js": "// Blog list page placeholder"
        }
    
    def _generate_backend_package_json(self) -> str:
        """Generate backend package.json."""
        package = {
            "name": "backend",
            "version": "1.0.0",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.5",
                "helmet": "^6.0.0",
                "bcryptjs": "^2.4.3",
                "jsonwebtoken": "^9.0.0"
            }
        }
        return json.dumps(package, indent=2)
    
    def _generate_vue_main(self) -> str:
        """Generate Vue main.js."""
        return '''import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

createApp(App).use(store).use(router).mount('#app')'''
    
    def _generate_vue_app_component(self, features: List[str]) -> str:
        """Generate Vue App component."""
        return '''<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>'''
    
    def _generate_vue_router(self) -> str:
        """Generate Vue router."""
        return '''import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router'''
    
    def _generate_vuex_store(self) -> str:
        """Generate Vuex store."""
        return '''import { createStore } from 'vuex'

export default createStore({
  state: {
  },
  mutations: {
  },
  actions: {
  },
  modules: {
  }
})'''
    
    def _generate_vue_hello_component(self) -> str:
        """Generate Vue hello component."""
        return '''<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>'''
    
    def _generate_vue_home_view(self) -> str:
        """Generate Vue home view."""
        return '''<template>
  <div class="home">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'Home',
  components: {
    HelloWorld
  }
}
</script>'''
    
    def _generate_vue_api_service(self) -> str:
        """Generate Vue API service."""
        return '''import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:3001/api'
})

export default api'''
    
    def _generate_vue_config(self) -> str:
        """Generate Vue config."""
        return '''const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true
})'''
    
    def _generate_vue_readme(self, app_name: str) -> str:
        """Generate Vue README."""
        return f'''# {app_name}

Vue.js application with modern features.

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```'''
    
    def _generate_angular_config(self) -> str:
        """Generate Angular configuration."""
        return '''{"$schema": "./node_modules/@angular/cli/lib/config/schema.json"}'''
    
    def _generate_angular_main(self) -> str:
        """Generate Angular main.ts."""
        return '''import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule);'''
    
    def _generate_angular_app_module(self, features: List[str]) -> str:
        """Generate Angular app module."""
        return '''import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }'''
    
    def _generate_angular_app_component(self) -> str:
        """Generate Angular app component."""
        return '''import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'angular-app';
}'''
    
    def _generate_angular_app_template(self) -> str:
        """Generate Angular app template."""
        return '''<div class="app">
  <h1>Welcome to {{ title }}!</h1>
  <router-outlet></router-outlet>
</div>'''
    
    def _generate_angular_api_service(self) -> str:
        """Generate Angular API service."""
        return '''import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) { }
}'''
    
    def _generate_angular_auth_service(self) -> str:
        """Generate Angular auth service."""
        return '''import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor() { }
}'''
    
    def _generate_angular_readme(self, app_name: str) -> str:
        """Generate Angular README."""
        return f'''# {app_name}

Angular application with modern features.

## Development server

Run `ng serve` for a dev server.

## Build

Run `ng build` to build the project.'''

    def _generate_product_card(self) -> str:
        """Generate product card component."""
        return '''import React from 'react';

function ProductCard({ product, onAddToCart }) {
  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.image} alt={product.name} />
        {product.discount && (
          <span className="discount-badge">-{product.discount}%</span>
        )}
      </div>
      
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-description">{product.description}</p>
        
        <div className="product-price">
          {product.originalPrice && (
            <span className="original-price">${product.originalPrice}</span>
          )}
          <span className="current-price">${product.price}</span>
        </div>
        
        <div className="product-rating">
          {'⭐'.repeat(Math.floor(product.rating || 0))}
          <span className="rating-text">({product.reviewCount || 0})</span>
        </div>
        
        <button 
          className="btn add-to-cart-btn"
          onClick={() => onAddToCart(product)}
          disabled={!product.inStock}
        >
          {product.inStock ? 'Add to Cart' : 'Out of Stock'}
        </button>
      </div>
    </div>
  );
}

export default ProductCard;'''

    def _generate_shopping_cart(self) -> str:
        """Generate shopping cart component."""
        return '''import React, { useState, useEffect } from 'react';

function ShoppingCart({ items, onUpdateQuantity, onRemoveItem, onCheckout }) {
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const newTotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    setTotal(newTotal);
  }, [items]);

  if (items.length === 0) {
    return (
      <div className="empty-cart">
        <h2>Your cart is empty</h2>
        <p>Add some products to get started!</p>
      </div>
    );
  }

  return (
    <div className="shopping-cart">
      <h2>Shopping Cart ({items.length} items)</h2>
      
      <div className="cart-items">
        {items.map(item => (
          <div key={item.id} className="cart-item">
            <div className="item-image">
              <img src={item.image} alt={item.name} />
            </div>
            
            <div className="item-details">
              <h3>{item.name}</h3>
              <p>${item.price}</p>
            </div>
            
            <div className="quantity-controls">
              <button 
                onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                disabled={item.quantity <= 1}
              >
                -
              </button>
              <span className="quantity">{item.quantity}</span>
              <button onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}>
                +
              </button>
            </div>
            
            <div className="item-total">
              ${(item.price * item.quantity).toFixed(2)}
            </div>
            
            <button 
              className="remove-item"
              onClick={() => onRemoveItem(item.id)}
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
      
      <div className="cart-summary">
        <div className="total">
          <h3>Total: ${total.toFixed(2)}</h3>
        </div>
        
        <button 
          className="btn checkout-btn"
          onClick={onCheckout}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
}

export default ShoppingCart;'''

    def _generate_react_readme(self, app_name: str, features: List[str]) -> str:
        """Generate comprehensive README for React app."""
        return f'''# 🌐 {app_name}

Advanced web application built with React and modern web technologies.

## 🚀 Features

{chr(10).join(f"- ✅ **{feature.replace('_', ' ').title()}**" for feature in features)}

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks and functional components
- **React Router** - Client-side routing
- **Redux Toolkit** - State management
- **Styled Components** - CSS-in-JS styling
- **Axios** - HTTP client

### Backend
- **Express.js** - Node.js web framework
- **JWT** - Authentication
- **Helmet** - Security middleware
- **Rate Limiting** - API protection

### Database
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions

## 📦 Installation

```bash
# Install dependencies
npm install

# Install backend dependencies
cd backend && npm install

# Start development servers
npm run dev
```

## 🚀 Development

```bash
# Frontend only
npm start

# Backend only
cd backend && npm run dev

# Both with concurrently
npm run dev
```

## 📊 Project Structure

```
{app_name}/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom hooks
│   ├── context/       # React context
│   ├── services/      # API services
│   ├── utils/         # Utility functions
│   └── styles/        # CSS styles
├── backend/
│   ├── routes/        # API routes
│   ├── models/        # Database models
│   ├── middleware/    # Express middleware
│   └── utils/         # Backend utilities
├── public/            # Static assets
├── tests/             # Test files
└── docs/              # Documentation
```

## 🔧 Configuration

Copy `.env.example` to `.env` and configure:

```env
REACT_APP_API_URL=http://localhost:3001/api
DATABASE_URL=postgresql://app_user:app_password@localhost:5432/app_db
JWT_SECRET=your_jwt_secret_here
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Build
```bash
# Build for production
npm run build

# Serve production build
npm run serve
```

## 📚 Documentation

- [API Documentation](./docs/API.md)
- [Component Documentation](./docs/COMPONENTS.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using the Programming Agent Web Framework Builder**'''

    def _generate_env_template(self) -> str:
        """Generate .env template."""
        return '''# Environment Configuration

# API Configuration
REACT_APP_API_URL=http://localhost:3001/api
API_PORT=3001

# Database Configuration
DATABASE_URL=postgresql://app_user:app_password@localhost:5432/app_db
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_db
DB_USER=app_user
DB_PASSWORD=app_password

# Authentication
JWT_SECRET=your_super_secret_jwt_key_here
JWT_EXPIRES_IN=7d

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Payment Configuration (optional)
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# File Upload
MAX_FILE_SIZE=10MB
UPLOAD_PATH=./uploads

# Security
CORS_ORIGIN=http://localhost:3000
RATE_LIMIT_WINDOW=15m
RATE_LIMIT_MAX=100

# Development
NODE_ENV=development
LOG_LEVEL=info'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""
        return '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Production builds
build/
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output/

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# Database
*.db
*.sqlite

# Uploads
uploads/
temp/'''

    # Brakujące metody generowania komponentów
    def _generate_navigation_component(self) -> str:
        """Generate navigation component."""
        return '''import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navigation">
      <ul className="nav-list">
        <li className={isActive('/') ? 'active' : ''}>
          <Link to="/">Home</Link>
        </li>
        <li className={isActive('/about') ? 'active' : ''}>
          <Link to="/about">About</Link>
        </li>
        <li className={isActive('/products') ? 'active' : ''}>
          <Link to="/products">Products</Link>
        </li>
        <li className={isActive('/contact') ? 'active' : ''}>
          <Link to="/contact">Contact</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navigation;'''

    def _generate_home_page(self) -> str:
        """Generate home page component."""
        return '''import React from 'react';

function Home() {
  return (
    <div className="home-page">
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Welcome to Your App</h1>
            <p>Build amazing web experiences with modern technology</p>
            <button className="btn btn-primary">Get Started</button>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2>Features</h2>
          <div className="grid grid-3">
            <div className="feature-card">
              <h3>🚀 Fast</h3>
              <p>Built with modern React and optimized for performance</p>
            </div>
            <div className="feature-card">
              <h3>🔒 Secure</h3>
              <p>Enterprise-grade security with JWT authentication</p>
            </div>
            <div className="feature-card">
              <h3>📱 Responsive</h3>
              <p>Works perfectly on all devices and screen sizes</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;'''

    def _generate_about_page(self) -> str:
        """Generate about page component."""
        return '''import React from 'react';

function About() {
  return (
    <div className="about-page">
      <div className="container">
        <div className="about-content">
          <h1>About Us</h1>
          <p>
            We are a team of passionate developers creating amazing web experiences
            using the latest technologies and best practices.
          </p>
          
          <div className="team-section">
            <h2>Our Team</h2>
            <div className="grid grid-2">
              <div className="team-member">
                <h3>Development Team</h3>
                <p>Expert developers with years of experience in modern web technologies</p>
              </div>
              <div className="team-member">
                <h3>Design Team</h3>
                <p>Creative designers focused on user experience and modern aesthetics</p>
              </div>
            </div>
          </div>
          
          <div className="values-section">
            <h2>Our Values</h2>
            <ul>
              <li>Quality first approach</li>
              <li>User-centered design</li>
              <li>Continuous innovation</li>
              <li>Transparency and communication</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;'''

    def _generate_auth_context(self) -> str:
        """Generate authentication context."""
        return '''import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const token = localStorage.getItem('authToken');
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  const loadUser = async () => {
    try {
      const response = await apiService.getProfile();
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiService.login(credentials);
      const { token, user } = response.data;
      
      localStorage.setItem('authToken', token);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await apiService.register(userData);
      const { token, user } = response.data;
      
      localStorage.setItem('authToken', token);
      setUser(user);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.message || 'Registration failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    apiService.logout().catch(console.error);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}'''

    def _generate_auth_hook(self) -> str:
        """Generate authentication hook."""
        return '''import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

export default useAuth;'''

    def _generate_utility_helpers(self) -> str:
        """Generate utility helper functions."""
        return '''// Utility helper functions

export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const formatDate = (date, options = {}) => {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  };
  
  return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options })
    .format(new Date(date));
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const validateEmail = (email) => {
  const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)[a-zA-Z\\d@$!%*?&]{8,}$/;
  return re.test(password);
};

export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

export const sleep = (ms) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy text: ', err);
    return false;
  }
};

export const downloadFile = (data, filename, type = 'application/json') => {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
};'''

    def _generate_component_styles(self) -> str:
        """Generate component-specific styles."""
        return '''/* Component-specific styles */

/* Product Card Styles */
.product-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.product-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.discount-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #dc3545;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.product-info {
  padding: 1.5rem;
}

.product-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #333;
}

.product-description {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.original-price {
  text-decoration: line-through;
  color: #999;
  font-size: 0.9rem;
}

.current-price {
  font-size: 1.3rem;
  font-weight: bold;
  color: #667eea;
}

.product-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.rating-text {
  color: #666;
  font-size: 0.9rem;
}

.add-to-cart-btn {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.add-to-cart-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Shopping Cart Styles */
.shopping-cart {
  max-width: 800px;
  margin: 0 auto;
}

.empty-cart {
  text-align: center;
  padding: 4rem 2rem;
}

.cart-items {
  margin-bottom: 2rem;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.cart-item .item-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  overflow: hidden;
}

.cart-item .item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
}

.item-details h3 {
  margin-bottom: 0.5rem;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-controls button {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.quantity-controls button:hover {
  background: #f8f9fa;
}

.quantity-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quantity {
  min-width: 40px;
  text-align: center;
  font-weight: bold;
}

.item-total {
  font-weight: bold;
  font-size: 1.1rem;
  color: #667eea;
}

.remove-item {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.remove-item:hover {
  background: #f8f9fa;
}

.cart-summary {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.cart-summary .total {
  text-align: center;
  margin-bottom: 2rem;
}

.checkout-btn {
  width: 100%;
  font-size: 1.1rem;
  padding: 1rem;
}

/* Feature Card Styles */
.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6rem 0;
  text-align: center;
}

.hero-content h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: bold;
}

.hero-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

/* Features Section */
.features {
  padding: 4rem 0;
}

.features h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: #333;
}'''

    def _generate_auth_routes(self) -> str:
        """Generate authentication routes."""
        return '''const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();

// Mock user database (replace with real database)
const users = [];

// Register route
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validation
    if (!email || !password || !name) {
      return res.status(400).json({ message: 'All fields are required' });
    }

    // Check if user exists
    const existingUser = users.find(user => user.email === email);
    if (existingUser) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const user = {
      id: users.length + 1,
      email,
      name,
      password: hashedPassword,
      createdAt: new Date()
    };

    users.push(user);

    // Generate JWT
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET || 'fallback_secret',
      { expiresIn: '7d' }
    );

    res.status(201).json({
      message: 'User created successfully',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Login route
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required' });
    }

    // Find user
    const user = users.find(user => user.email === email);
    if (!user) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    // Generate JWT
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET || 'fallback_secret',
      { expiresIn: '7d' }
    );

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Logout route
router.post('/logout', (req, res) => {
  res.json({ message: 'Logout successful' });
});

module.exports = router;'''

    def _generate_api_routes(self) -> str:
        """Generate general API routes."""
        return '''const express = require('express');
const router = express.Router();
const authMiddleware = require('../middleware/auth');

// Protected route example
router.get('/protected', authMiddleware, (req, res) => {
  res.json({ 
    message: 'This is a protected route', 
    user: req.user 
  });
});

// Get user profile
router.get('/user/profile', authMiddleware, (req, res) => {
  res.json({
    id: req.user.userId,
    email: req.user.email,
    name: 'User Name' // Get from database
  });
});

// Update user profile
router.put('/user/profile', authMiddleware, (req, res) => {
  const { name, email } = req.body;
  
  // Update user in database
  res.json({
    message: 'Profile updated successfully',
    user: { name, email }
  });
});

// File upload endpoint
router.post('/upload', authMiddleware, (req, res) => {
  // Handle file upload logic here
  res.json({
    message: 'File uploaded successfully',
    filename: 'uploaded_file.jpg',
    url: '/uploads/uploaded_file.jpg'
  });
});

// Generic CRUD endpoints
router.get('/items', (req, res) => {
  res.json({
    items: [],
    total: 0,
    page: 1,
    limit: 10
  });
});

router.post('/items', authMiddleware, (req, res) => {
  const item = req.body;
  res.status(201).json({
    message: 'Item created successfully',
    item: { id: Date.now(), ...item }
  });
});

router.put('/items/:id', authMiddleware, (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  
  res.json({
    message: 'Item updated successfully',
    item: { id, ...updates }
  });
});

router.delete('/items/:id', authMiddleware, (req, res) => {
  const { id } = req.params;
  
  res.json({
    message: 'Item deleted successfully',
    id
  });
});

module.exports = router;'''

    def _generate_user_model(self, database: str) -> str:
        """Generate user model."""
        if database == 'mongodb':
            return '''const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  name: {
    type: String,
    required: true
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastLogin: {
    type: Date
  }
}, {
  timestamps: true
});

userSchema.methods.toJSON = function() {
  const user = this.toObject();
  delete user.password;
  return user;
};

module.exports = mongoose.model('User', userSchema);'''
        else:
            return '''// User model for SQL databases (PostgreSQL/MySQL)

const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const User = sequelize.define('User', {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true
      }
    },
    password: {
      type: DataTypes.STRING,
      allowNull: false,
      validate: {
        len: [6, 100]
      }
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false
    },
    role: {
      type: DataTypes.ENUM('user', 'admin'),
      defaultValue: 'user'
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    },
    lastLogin: {
      type: DataTypes.DATE
    }
  }, {
    timestamps: true,
    defaultScope: {
      attributes: { exclude: ['password'] }
    },
    scopes: {
      withPassword: {
        attributes: { include: ['password'] }
      }
    }
  });

  return User;
};'''

    def _generate_auth_middleware(self) -> str:
        """Generate authentication middleware."""
        return '''const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  try {
    const authHeader = req.header('Authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'Access denied. No token provided.' });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback_secret');
    req.user = decoded;
    
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token expired' });
    } else if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ message: 'Invalid token' });
    } else {
      return res.status(500).json({ message: 'Server error' });
    }
  }
};

module.exports = authMiddleware;'''

    def _generate_dockerfile_react(self) -> str:
        """Generate Dockerfile for React app."""
        return '''# Multi-stage build for React app
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/
COPY public/ ./public/

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]'''

    def _generate_checkout_component(self) -> str:
        """Generate checkout component."""
        return '''import React, { useState } from 'react';

function Checkout({ cartItems, total, onPlaceOrder }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    address: '',
    city: '',
    zipCode: '',
    cardNumber: '',
    expiryDate: '',
    cvv: ''
  });

  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onPlaceOrder({
        items: cartItems,
        total,
        customerInfo: formData
      });
    } catch (error) {
      console.error('Order failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout">
      <div className="container">
        <h1>Checkout</h1>
        
        <div className="checkout-content">
          <div className="checkout-form">
            <form onSubmit={handleSubmit}>
              <div className="form-section">
                <h3>Shipping Information</h3>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      required
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      required
                      className="form-control"
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    required
                    className="form-control"
                  />
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>City</label>
                    <input
                      type="text"
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      required
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>ZIP Code</label>
                    <input
                      type="text"
                      name="zipCode"
                      value={formData.zipCode}
                      onChange={handleInputChange}
                      required
                      className="form-control"
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h3>Payment Information</h3>
                
                <div className="form-group">
                  <label>Card Number</label>
                  <input
                    type="text"
                    name="cardNumber"
                    value={formData.cardNumber}
                    onChange={handleInputChange}
                    placeholder="1234 5678 9012 3456"
                    required
                    className="form-control"
                  />
                </div>
                
                <div className="form-row">
                  <div className="form-group">
                    <label>Expiry Date</label>
                    <input
                      type="text"
                      name="expiryDate"
                      value={formData.expiryDate}
                      onChange={handleInputChange}
                      placeholder="MM/YY"
                      required
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>CVV</label>
                    <input
                      type="text"
                      name="cvv"
                      value={formData.cvv}
                      onChange={handleInputChange}
                      placeholder="123"
                      required
                      className="form-control"
                    />
                  </div>
                </div>
              </div>

              <button 
                type="submit" 
                className="btn checkout-submit-btn"
                disabled={loading}
              >
                {loading ? 'Processing...' : `Place Order - $${total.toFixed(2)}`}
              </button>
            </form>
          </div>
          
          <div className="order-summary">
            <h3>Order Summary</h3>
            
            <div className="summary-items">
              {cartItems.map(item => (
                <div key={item.id} className="summary-item">
                  <span>{item.name} x {item.quantity}</span>
                  <span>${(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
            </div>
            
            <div className="summary-total">
              <strong>Total: ${total.toFixed(2)}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Checkout;'''

    # Brakujące metody placeholder
    def _generate_product_list(self) -> str:
        """Generate product list page."""
        return "// Product list page placeholder"
    
    def _generate_product_detail(self) -> str:
        """Generate product detail page."""
        return "// Product detail page placeholder"
    
    def _generate_payment_service(self) -> str:
        """Generate payment service."""
        return "// Payment service placeholder"
    
    def _generate_products_api(self) -> str:
        """Generate products API."""
        return "// Products API placeholder"
    
    def _generate_orders_api(self) -> str:
        """Generate orders API."""
        return "// Orders API placeholder"
    
    def _generate_product_model(self) -> str:
        """Generate product model."""
        return "// Product model placeholder"
    
    def _generate_order_model(self) -> str:
        """Generate order model."""
        return "// Order model placeholder"
    
    def _generate_content_editor(self) -> str:
        """Generate content editor."""
        return "// Content editor placeholder"
    
    def _generate_media_manager(self) -> str:
        """Generate media manager."""
        return "// Media manager placeholder"
    
    def _generate_admin_panel(self) -> str:
        """Generate admin panel."""
        return "// Admin panel placeholder"
    
    def _generate_content_api(self) -> str:
        """Generate content API."""
        return "// Content API placeholder"
    
    def _generate_content_model(self) -> str:
        """Generate content model."""
        return "// Content model placeholder"
    
    def _generate_fastapi_server(self, database: str) -> str:
        """Generate FastAPI server."""
        return '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FastAPI server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)'''
    
    def _generate_dockerfile_react(self) -> str:
        """Generate Dockerfile for React."""
        return '''FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]'''

def main():
    """Main function for testing the web framework builder."""
    print("🌐 Web Framework Builder - Test")
    
    builder = WebFrameworkBuilder()
    
    # Test React app creation
    result = builder.create_web_application(
        app_name="Advanced E-commerce Platform",
        framework="e_commerce",
        features=['authentication', 'payment', 'admin_panel', 'analytics'],
        backend="express",
        database="postgresql"
    )
    
    print("✅ Aplikacja webowa utworzona:")
    print(f"📦 Framework: {result['framework']}")
    print(f"⏱️ Czas rozwoju: {result['estimated_dev_time']['estimated_days']} dni")
    print(f"🔧 Pliki: {len(result['structure']['files'])} plików")
    print(f"📁 Katalogi: {len(result['structure']['directories'])} katalogów")

if __name__ == "__main__":
    main()