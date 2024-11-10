// frontend/src/components/contacts/ImportExport.jsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, Download, X, Check } from 'lucide-react';

const ImportExport = ({ onClose, onImport }) => {
  const [previewData, setPreviewData] = useState([]);
  const [error, setError] = useState('');

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.vcf')) {
      setError('Please upload a valid vCard file (.vcf)');
      return;
    }

    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        // Process vCard data here
        setPreviewData([
          // Sample preview data
          { id: 1, first_name: 'John', last_name: 'Doe', status: 'new' },
          { id: 2, first_name: 'Jane', last_name: 'Smith', status: 'duplicate' }
        ]);
      };
      reader.readAsText(file);
    } catch (err) {
      setError('Error reading file');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Import/Export Contacts</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <Input
              type="file"
              accept=".vcf"
              onChange={handleFileUpload}
            />

            {previewData.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-medium">Preview</h3>
                <div className="divide-y border rounded-lg">
                  {previewData.map(contact => (
                    <div key={contact.id} className="p-4 flex justify-between items-center">
                      <div>
                        <p className="font-medium">
                          {contact.first_name} {contact.last_name}
                        </p>
                        <p className="text-sm text-gray-500">
                          Status: {contact.status}
                        </p>
                      </div>
                      {contact.status === 'duplicate' && (
                        <Button size="sm" variant="outline">
                          Review
                        </Button>
                      )}
                    </div>
                  ))}
                </div>

                <div className="flex justify-end space-x-2">
                  <Button variant="outline" onClick={onClose}>
                    Cancel
                  </Button>
                  <Button onClick={() => onImport(previewData)}>
                    Import Selected
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ImportExport;
