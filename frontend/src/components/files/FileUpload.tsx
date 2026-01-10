import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '../common/Button';

interface FileUploadProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUpload, isUploading }) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      for (const file of acceptedFiles) {
        await onUpload(file);
      }
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
        ${isDragActive
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }
        ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
      `}
    >
      <input {...getInputProps()} />

      <div className="flex flex-col items-center">
        <svg
          className="w-16 h-16 text-gray-400 mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        {isDragActive ? (
          <p className="text-lg text-blue-600 font-semibold">
            Отпустите файлы здесь...
          </p>
        ) : (
          <>
            <p className="text-lg text-gray-700 font-semibold mb-2">
              Перетащите файлы сюда
            </p>
            <p className="text-sm text-gray-500 mb-4">
              или нажмите для выбора файлов
            </p>
            <Button variant="primary" size="sm" disabled={isUploading}>
              Выбрать файлы
            </Button>
          </>
        )}

        {isUploading && (
          <p className="text-sm text-gray-500 mt-4">Загрузка файла...</p>
        )}
      </div>
    </div>
  );
};
