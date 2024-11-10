// frontend/src/components/search/SearchBar.jsx
import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from '@/components/ui/card';
import { Search, Filter, X } from 'lucide-react';

const SearchBar = ({ onSearch, onFilter }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    tags: [],
    sortBy: 'name'
  });

  const handleSearch = (value) => {
    setSearchTerm(value);
    onSearch(value, activeFilters);
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...activeFilters, [key]: value };
    setActiveFilters(newFilters);
    onFilter(newFilters);
  };

  const clearFilters = () => {
    const resetFilters = {
      tags: [],
      sortBy: 'name'
    };
    setActiveFilters(resetFilters);
    onFilter(resetFilters);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search contacts..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={activeFilters.sortBy}
          onValueChange={(value) => handleFilterChange('sortBy', value)}
        >
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="recent">Recently Added</SelectItem>
            <SelectItem value="company">Company</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {(activeFilters.tags.length > 0 || activeFilters.sortBy !== 'name') && (
        <Card className="p-2">
          <div className="flex flex-wrap gap-2 items-center text-sm">
            <span className="text-gray-500">Active filters:</span>
            {activeFilters.tags.map((tag) => (
              <Button
                key={tag}
                variant="secondary"
                size="sm"
                onClick={() => handleFilterChange('tags', 
                  activeFilters.tags.filter(t => t !== tag)
                )}
                className="h-6 px-2 flex items-center"
              >
                {tag}
                <X className="h-3 w-3 ml-1" />
              </Button>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="h-6 px-2"
            >
              Clear all
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default SearchBar;
