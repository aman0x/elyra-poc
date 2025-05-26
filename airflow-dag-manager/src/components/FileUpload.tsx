import React, { useState, useRef, useCallback } from 'react';
import { minioService } from '../services/minioService';

interface FileUploadProps {
  onUploadSuccess?: (fileName: string, fileUrl: string) => void;
  onUploadError?: (error: string) => void;
  allowedTypes?: string[];
  maxFileSize?: number; // in MB
  dagId?: string; // Optional DAG ID for organizing files
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  allowedTypes = ['.py', '.sql', '.json', '.yaml', '.yml', '.txt'],
  maxFileSize = 10, // 10MB default
  dagId
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size must be less than ${maxFileSize}MB`;
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (allowedTypes.length > 0 && !allowedTypes.includes(fileExtension)) {
      return `File type not allowed. Allowed types: ${allowedTypes.join(', ')}`;
    }

    return null;
  };

  const generateFileName = (file: File): string => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const extension = file.name.split('.').pop();
    const baseName = file.name.replace(/\.[^/.]+$/, '');
    
    if (dagId) {
      return `${dagId}/${baseName}_${timestamp}.${extension}`;
    }
    
    return `${baseName}_${timestamp}.${extension}`;
  };

  const uploadFile = async (file: File) => {
    const validation = validateFile(file);
    if (validation) {
      onUploadError?.(validation);
      return;
    }

    const uploadingFile: UploadingFile = {
      file,
      progress: 0,
      status: 'uploading'
    };

    setUploadingFiles(prev => [...prev, uploadingFile]);

    try {
      const fileName = generateFileName(file);
      
      const fileUrl = await minioService.uploadFileWithProgress(
        file,
        fileName,
        (progress) => {
          setUploadingFiles(prev => 
            prev.map(f => 
              f.file === file 
                ? { ...f, progress }
                : f
            )
          );
        }
      );

      // Update status to success
      setUploadingFiles(prev => 
        prev.map(f => 
          f.file === file 
            ? { ...f, status: 'success', progress: 100 }
            : f
        )
      );

      onUploadSuccess?.(fileName, fileUrl);

      // Remove from uploading list after 2 seconds
      setTimeout(() => {
        setUploadingFiles(prev => prev.filter(f => f.file !== file));
      }, 2000);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      
      setUploadingFiles(prev => 
        prev.map(f => 
          f.file === file 
            ? { ...f, status: 'error', error: errorMessage }
            : f
        )
      );

      onUploadError?.(errorMessage);
    }
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    Array.from(files).forEach(uploadFile);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    // Reset input value to allow uploading the same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [handleFiles]);

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload">
      <div
        className={`upload-zone ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <div className="upload-icon">📁</div>
        <div className="upload-text">
          <p className="primary-text">Drop files here or click to browse</p>
          <p className="secondary-text">
            Supported: {allowedTypes.join(', ')} | Max size: {maxFileSize}MB
          </p>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={allowedTypes.join(',')}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {uploadingFiles.length > 0 && (
        <div className="upload-progress">
          <h4>Uploading Files</h4>
          {uploadingFiles.map((uploadingFile, index) => (
            <div key={index} className="progress-item">
              <div className="file-info">
                <span className="file-name">{uploadingFile.file.name}</span>
                <span className={`status ${uploadingFile.status}`}>
                  {uploadingFile.status === 'uploading' && '⏳'}
                  {uploadingFile.status === 'success' && '✅'}
                  {uploadingFile.status === 'error' && '❌'}
                </span>
              </div>
              
              {uploadingFile.status === 'uploading' && (
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${uploadingFile.progress}%` }}
                  ></div>
                </div>
              )}
              
              {uploadingFile.status === 'error' && (
                <div className="error-text">{uploadingFile.error}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;