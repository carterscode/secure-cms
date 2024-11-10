// frontend/src/components/contacts/ContactList.jsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Upload, Download } from 'lucide-react';

const ContactList = ({ contacts, onSelectContact, onNewContact, onImport, onExport }) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Contacts</h2>
        <div className="flex space-x-2">
          <Button onClick={onNewContact}>
            <Plus className="h-4 w-4 mr-2" />
            New Contact
          </Button>
          <Button variant="outline" onClick={onImport}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button variant="outline" onClick={onExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {contacts.map(contact => (
          <Card 
            key={contact.id} 
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => onSelectContact(contact)}
          >
            <CardContent className="p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">
                    {contact.first_name} {contact.last_name}
                  </h3>
                  <p className="text-sm text-gray-500">{contact.email}</p>
                  <p className="text-sm text-gray-500">{contact.phone}</p>
                </div>
                <div className="flex gap-2">
                  {contact.tags?.map(tag => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ContactList;
