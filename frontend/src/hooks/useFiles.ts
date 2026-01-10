import { useState, useEffect } from 'react';
import { filesAPI } from '../services/api';
import toast from 'react-hot-toast';
import type { FileItem } from '../types';

export const useFiles = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [totalFiles, setTotalFiles] = useState(0);

  const loadFiles = async (folder: string = 'root') => {
    setIsLoading(true);
    try {
      const response = await filesAPI.list(folder);
      console.log('API Response:', response); // Для отладки

      // Backend возвращает массив напрямую
      if (Array.isArray(response)) {
        setFiles(response);
        setTotalFiles(response.length);
      } else if (response.files) {
        setFiles(response.files);
        setTotalFiles(response.total || 0);
      }
    } catch (error: any) {
      console.error('Load files error:', error);
      toast.error('Ошибка загрузки файлов');
    } finally {
      setIsLoading(false);
    }
  };

  const uploadFile = async (file: File) => {
    try {
      const response = await filesAPI.upload(file);
      toast.success(`Файл "${file.name}" загружен!`);
      await loadFiles();
      return response;
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки');
      throw error;
    }
  };

  const deleteFile = async (fileId: string, filename: string) => {
    try {
      await filesAPI.delete(fileId);
      toast.success(`Файл "${filename}" удалён`);
      await loadFiles();
    } catch (error: any) {
      toast.error('Ошибка удаления файла');
    }
  };

  const downloadFile = async (fileId: string, filename: string) => {
    try {
      const response = await filesAPI.download(fileId);
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success(`Файл "${filename}" скачан`);
    } catch (error: any) {
      toast.error('Ошибка скачивания файла');
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  return {
    files,
    isLoading,
    totalFiles,
    loadFiles,
    uploadFile,
    deleteFile,
    downloadFile,
  };
};
