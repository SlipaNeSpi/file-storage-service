import React from 'react';
import { FileItem } from './FileItem';
import { LoadingSpinner } from '../common/LoadingSpinner';

interface FileListProps {
  files: any[];
  isLoading: boolean;
  onDownload: (id: string, filename: string) => void;
  onDelete: (id: string, filename: string) => void;
}

export const FileList: React.FC<FileListProps> = ({
  files,
  isLoading,
  onDownload,
  onDelete,
}) => {
  if (isLoading) {
    return <LoadingSpinner text="Загрузка файлов..." />;
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">
          📂 Файлов пока нет
        </p>
        <p className="text-gray-400 text-sm mt-2">
          Загрузите первый файл, используя форму выше
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {files.map((file) => (
        <FileItem
          key={file.id}
          file={file}
          onDownload={onDownload}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};
