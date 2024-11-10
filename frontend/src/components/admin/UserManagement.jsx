// frontend/src/components/admin/UserManagement.jsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Switch } from '@/components/ui/switch';
import { UserPlus, Lock, Shield, User, X, Check, AlertCircle } from 'lucide-react';

const UserManagement = () => {
  const [users, setUsers] = useState([
    { id: 1, name: 'Admin User', email: 'admin@example.com', isAdmin: true, isActive: true },
    { id: 2, name: 'Regular User', email: 'user@example.com', isAdmin: false, isActive: true },
  ]);
  const [showNewUserDialog, setShowNewUserDialog] = useState(false);
  const [newUser, setNewUser] = useState({ name: '', email: '', isAdmin: false });
  const [error, setError] = useState('');

  const handleToggleUserStatus = (userId) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, isActive: !user.isActive }
        : user
    ));
  };

  const handleToggleAdminStatus = (userId) => {
    setUsers(users.map(user => 
      user.id === userId 
        ? { ...user, isAdmin: !user.isAdmin }
        : user
    ));
  };

  const handleAddUser = () => {
    if (!newUser.name || !newUser.email) {
      setError('Please fill in all required fields');
      return;
    }

    setUsers([
      ...users,
      {
        id: Date.now(),
        ...newUser,
        isActive: true
      }
    ]);
    setNewUser({ name: '', email: '', isAdmin: false });
    setShowNewUserDialog(false);
    setError('');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">User Management</h2>
        <Dialog open={showNewUserDialog} onOpenChange={setShowNewUserDialog}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Add User
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New User</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div>
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="admin"
                  checked={newUser.isAdmin}
                  onCheckedChange={(checked) => setNewUser({ ...newUser, isAdmin: checked })}
                />
                <Label htmlFor="admin">Admin privileges</Label>
              </div>
              <Button onClick={handleAddUser} className="w-full">
                Add User
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent>
          <div className="relative overflow-x-auto">
            <div className="grid grid-cols-4 font-medium p-4 bg-gray-50 border-b">
              <div>User</div>
              <div>Role</div>
              <div>Status</div>
              <div>Actions</div>
            </div>
            <div className="divide-y">
              {users.map((user) => (
                <div key={user.id} className="grid grid-cols-4 p-4 items-center">
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4" />
                    <div>
                      <div className="font-medium">{user.name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </div>
                  <div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.isAdmin ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {user.isAdmin ? 'Admin' : 'User'}
                    </span>
                  </div>
                  <div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleAdminStatus(user.id)}
                    >
                      <Shield className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleUserStatus(user.id)}
                    >
                      {user.isActive ? (
                        <X className="h-4 w-4" />
                      ) : (
                        <Check className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                    >
                      <Lock className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserManagement;
