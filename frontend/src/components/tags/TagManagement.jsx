import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tag, Plus, X, Edit2 } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const TagManagement = ({ onClose }) => {
  const [tags, setTags] = useState([
    { id: 1, name: 'Work', contactCount: 15 },
    { id: 2, name: 'Family', contactCount: 8 },
    { id: 3, name: 'Friends', contactCount: 12 }
  ]);
  const [newTag, setNewTag] = useState('');
  const [editingTag, setEditingTag] = useState(null);
  const [error, setError] = useState('');

  const handleAddTag = () => {
    if (!newTag.trim()) {
      setError('Tag name cannot be empty');
      return;
    }

    if (tags.some(tag => tag.name.toLowerCase() === newTag.toLowerCase())) {
      setError('Tag already exists');
      return;
    }

    setTags([
      ...tags,
      {
        id: Date.now(),
        name: newTag.trim(),
        contactCount: 0
      }
    ]);
    setNewTag('');
    setError('');
  };

  const handleDeleteTag = (tagId) => {
    setTags(tags.filter(tag => tag.id !== tagId));
  };

  const handleEditTag = (tag) => {
    setEditingTag(tag);
  };

  const handleUpdateTag = () => {
    if (!editingTag.name.trim()) {
      setError('Tag name cannot be empty');
      return;
    }

    if (tags.some(tag => 
      tag.id !== editingTag.id && 
      tag.name.toLowerCase() === editingTag.name.toLowerCase()
    )) {
      setError('Tag already exists');
      return;
    }

    setTags(tags.map(tag =>
      tag.id === editingTag.id ? editingTag : tag
    ));
    setEditingTag(null);
    setError('');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>
            <div className="flex items-center">
              <Tag className="h-5 w-5 mr-2" />
              Manage Tags
            </div>
          </CardTitle>
          <Button variant="outline" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Enter new tag name"
              className="flex-1"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
            />
            <Button onClick={handleAddTag}>
              <Plus className="h-4 w-4 mr-2" />
              Add Tag
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tag Name</TableHead>
                <TableHead>Contacts</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tags.map((tag) => (
                <TableRow key={tag.id}>
                  <TableCell>
                    {editingTag?.id === tag.id ? (
                      <Input
                        value={editingTag.name}
                        onChange={(e) => setEditingTag({
                          ...editingTag,
                          name: e.target.value
                        })}
                        className="max-w-[200px]"
                      />
                    ) : (
                      <span className="flex items-center">
                        <Tag className="h-4 w-4 mr-2" />
                        {tag.name}
                      </span>
                    )}
                  </TableCell>
                  <TableCell>{tag.contactCount} contacts</TableCell>
                  <TableCell className="text-right">
                    {editingTag?.id === tag.id ? (
                      <div className="space-x-2">
                        <Button
                          size="sm"
                          onClick={handleUpdateTag}
                        >
                          Save
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEditingTag(null)}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : (
                      <div className="space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditTag(tag)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteTag(tag.id)}
                          disabled={tag.contactCount > 0}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default TagManagement;
