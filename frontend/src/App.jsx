// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Import our components
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import ContactList from './components/contacts/ContactList';
import ContactForm from './components/contacts/ContactForm';
import ImportExport from './components/contacts/ImportExport';
import Profile from './components/profile/Profile';
import TagManagement from './components/tags/TagManagement';
import SearchBar from './components/search/SearchBar';
import { UserManagement, AuditLog } from './components/admin';
import { LoadingState } from './components/ui/LoadingState';
import { ToastContainer } from './components/ui/NotificationToast';

const App = () => {
  // Application state
  const [currentView, setCurrentView] = useState('contacts');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [selectedContact, setSelectedContact] = useState(null);
  const [showContactForm, setShowContactForm] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [user, setUser] = useState(null);

  // Initialize the application
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Simulate loading user data
        await new Promise(resolve => setTimeout(resolve, 1000));
        setUser({
          name: 'Admin User',
          email: 'admin@example.com',
          isAdmin: true,
          avatarUrl: null
        });
        setLoading(false);
      } catch (error) {
        showToast('Error loading application', 'error');
        setLoading(false);
      }
    };

    initializeApp();
  }, []);

  // Toast management
  const showToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  // Auth handlers
  const handleLogin = async (credentials) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsAuthenticated(true);
      showToast('Welcome back!', 'success');
    } catch (error) {
      showToast('Invalid credentials', 'error');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUser(null);
    showToast('Logged out successfully', 'info');
  };

  // Render loading state
  if (loading) {
    return <LoadingState type="card" count={3} />;
  }

  // Render login screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 space-y-4">
            <h1 className="text-2xl font-bold text-center">Secure CMS</h1>
            <form onSubmit={(e) => {
              e.preventDefault();
              handleLogin();
            }} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required />
              </div>
              <Button type="submit" className="w-full">
                Sign In
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Render main application
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar
        user={user}
        onLogout={handleLogout}
        onMenuToggle={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        onProfileClick={() => setCurrentView('profile')}
        onSettingsClick={() => setCurrentView('settings')}
        onAdminPanelClick={() => setCurrentView('admin')}
      />

      <Sidebar
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        onNavigate={setCurrentView}
        currentView={currentView}
        isAdmin={user?.isAdmin}
      />

      <main className={`
        transition-all duration-200 ease-in-out
        md:ml-64 pt-16
      `}>
        <div className="max-w-7xl mx-auto p-4 space-y-4">
          {/* Render current view */}
          {currentView === 'contacts' && (
            <>
              <SearchBar 
                onSearch={(term) => console.log('Searching:', term)}
                onFilter={(filters) => console.log('Filters:', filters)}
              />
              <ContactList
                contacts={[]}
                onSelectContact={setSelectedContact}
                onNewContact={() => setShowContactForm(true)}
                onImport={() => setShowImportDialog(true)}
                onExport={() => {}}
              />
            </>
          )}

          {currentView === 'profile' && <Profile user={user} />}
          {currentView === 'tags' && <TagManagement />}
          {currentView === 'admin' && user?.isAdmin && <UserManagement />}
          {currentView === 'audit' && user?.isAdmin && <AuditLog />}
        </div>
      </main>

      {/* Modals */}
      {showContactForm && (
        <ContactForm
          contact={selectedContact}
          onSave={(data) => {
            console.log('Saving contact:', data);
            setShowContactForm(false);
            showToast('Contact saved successfully', 'success');
          }}
          onCancel={() => setShowContactForm(false)}
        />
      )}

      {showImportDialog && (
        <ImportExport
          onClose={() => setShowImportDialog(false)}
          onImport={(data) => {
            console.log('Importing contacts:', data);
            setShowImportDialog(false);
            showToast('Contacts imported successfully', 'success');
          }}
        />
      )}

      {/* Toasts */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
};

export default App;
