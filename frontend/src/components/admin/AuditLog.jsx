// frontend/src/components/admin/AuditLog.jsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Clock, Search, Filter } from 'lucide-react';

const AuditLog = () => {
  const [logs, setLogs] = useState([
    {
      id: 1,
      action: 'User Login',
      user: 'admin@example.com',
      timestamp: new Date().toISOString(),
      details: 'Successful login attempt',
      ip: '192.168.1.1'
    },
    {
      id: 2,
      action: 'Contact Created',
      user: 'user@example.com',
      timestamp: new Date().toISOString(),
      details: 'Created new contact: John Doe',
      ip: '192.168.1.2'
    }
  ]);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.details.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    
    return matchesSearch && matchesAction;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Audit Log</h2>
        <div className="flex space-x-2">
          <div className="relative w-64">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={actionFilter} onValueChange={setActionFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Filter by action" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Actions</SelectItem>
              <SelectItem value="User Login">User Login</SelectItem>
              <SelectItem value="Contact Created">Contact Created</SelectItem>
              <SelectItem value="Contact Updated">Contact Updated</SelectItem>
              <SelectItem value="Contact Deleted">Contact Deleted</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardContent>
          <div className="relative overflow-x-auto">
            <div className="grid grid-cols-4 font-medium p-4 bg-gray-50 border-b">
              <div>Action</div>
              <div>User</div>
              <div>Timestamp</div>
              <div>Details</div>
            </div>
            <div className="divide-y">
              {filteredLogs.map((log) => (
                <div key={log.id} className="grid grid-cols-4 p-4">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="font-medium">{log.action}</span>
                  </div>
                  <div>{log.user}</div>
                  <div>{formatDate(log.timestamp)}</div>
                  <div>
                    <div>{log.details}</div>
                    <div className="text-sm text-gray-500">IP: {log.ip}</div>
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

export default AuditLog;
