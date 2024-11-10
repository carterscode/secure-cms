// frontend/src/components/layout/Sidebar.jsx
import React from 'react';
import { Button } from '@/components/ui/button';
import { User, Tags, Clock, Settings, X } from 'lucide-react';

const Sidebar = ({ 
  isOpen, 
  onClose, 
  onNavigate, 
  currentView, 
  isAdmin 
}) => {
  const menuItems = [
    { 
      id: 'contacts',
      icon: User, 
      label: 'Contacts', 
      onClick: () => onNavigate('contacts')
    },
    { 
      id: 'tags',
      icon: Tags, 
      label: 'Tags', 
      onClick: () => onNavigate('tags')
    },
    { 
      id: 'settings',
      icon: Settings, 
      label: 'Settings', 
      onClick: () => onNavigate('settings')
    },
  ];

  // Add audit log for admin users
  if (isAdmin) {
    menuItems.push({
      id: 'audit',
      icon: Clock,
      label: 'Audit Log',
      onClick: () => onNavigate('audit')
    });
  }

  return (
    <aside className={`
      fixed inset-y-0 left-0 z-30 w-64 bg-white border-r transform 
      transition-transform duration-200 ease-in-out pt-16
      ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      md:translate-x-0
    `}>
      <div className="h-16 flex items-center justify-between px-4 md:hidden">
        <h2 className="text-lg font-semibold">Menu</h2>
        <Button 
          variant="ghost" 
          size="icon"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      <nav className="p-4 space-y-2">
        {menuItems.map((item) => (
          <Button
            key={item.id}
            variant={currentView === item.id ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => {
              item.onClick();
              if (window.innerWidth < 768) onClose();
            }}
          >
            <item.icon className="mr-2 h-4 w-4" />
            {item.label}
          </Button>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
