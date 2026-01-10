import React from 'react';
import { formatFileSize, formatDate } from '../../utils/formatters';
import { Button } from '../common/Button';

interface FileItemProps {
  file: {
    id: string;
    filename: string;
    size: number;      // ← Было file_size
    type: string;      // ← Было file_type
    created_at: string;
  };
  onDownload: (id: string, filename: string) => void;
  onDelete: (id: string, filename: string) => void;
}

export const FileItem: React.FC<FileItemProps> = ({ file, onDownload, onDelete }) => {
  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('image')) return '🖼️';
    if (type.includes('video')) return '🎥';
    if (type.includes('audio')) return '🎵';
    if (type.includes('zip') || type.includes('rar')) return '📦';
    if (type.includes('text')) return '📝';
    if (type.includes('word') || type.includes('doc')) return '📘';
    if (type.includes('sheet') || type.includes('excel')) return '📊';
    return '📄';
  };

  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center space-x-4 flex-1 min-w-0">
        <span className="text-3xl">{getFileIcon(file.type)}</span>

        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate">
            {file.filename}
          </h3>
          <p className="text-xs text-gray-500">
            {formatFileSize(file.size)} • {formatDate(file.created_at)}
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-2 ml-4">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onDownload(file.id, file.filename)}
        >
          ⬇️ Скачать
        </Button>
        <Button
          variant="danger"
          size="sm"
          onClick={() => onDelete(file.id, file.filename)}
        >
          🗑️ Удалить
        </Button>
      </div>
    </div>
  );
};
