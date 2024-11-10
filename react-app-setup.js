// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/auth/Login';
import TwoFactorAuth from './pages/auth/TwoFactorAuth';
import Register from './pages/auth/Register';
import ContactList from './pages/contacts/ContactList';
import ContactDetail from './pages/contacts/ContactDetail';
import ContactForm from './pages/contacts/ContactForm';
import ImportContacts from './pages/contacts/ImportContacts';
import Settings from './pages/settings/Settings';
import Layout from './components/layout/Layout';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/2fa" element={<TwoFactorAuth />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Layout>
                  <ContactList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/contacts"
            element={
              <PrivateRoute>
                <Layout>
                  <ContactList />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/contacts/new"
            element={
              <PrivateRoute>
                <Layout>
                  <ContactForm />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/contacts/:id"
            element={
              <PrivateRoute>
                <Layout>
                  <ContactDetail />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/contacts/:id/edit"
            element={
              <PrivateRoute>
                <Layout>
                  <ContactForm />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/import"
            element={
              <PrivateRoute>
                <Layout>
                  <ImportContacts />
                </Layout>
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Layout>
                  <Settings />
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
