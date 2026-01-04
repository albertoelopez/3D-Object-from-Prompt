import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';

interface ImageUploadProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

export function ImageUpload({ file, onFileChange, disabled }: ImageUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileChange(acceptedFiles[0]);
      }
    },
    [onFileChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/webp': ['.webp'],
    },
    maxFiles: 1,
    disabled,
  });

  const removeFile = () => {
    onFileChange(null);
  };

  if (file) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Selected Image
        </label>
        <div className="relative p-4 bg-black/30 border border-white/10 rounded-lg">
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-lg overflow-hidden bg-gray-800 flex items-center justify-center">
              <img
                src={URL.createObjectURL(file)}
                alt="Preview"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1">
              <p className="text-white font-medium truncate">{file.name}</p>
              <p className="text-sm text-gray-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={removeFile}
              disabled={disabled}
              className="p-2 text-gray-400 hover:text-red-400 transition-colors disabled:opacity-50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">
        Upload an image
      </label>
      <div
        {...getRootProps()}
        className={`p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-white/10 hover:border-white/30 bg-black/30'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          {isDragActive ? (
            <ImageIcon className="w-12 h-12 text-primary-400" />
          ) : (
            <Upload className="w-12 h-12 text-gray-500" />
          )}
          <div>
            <p className="text-white font-medium">
              {isDragActive ? 'Drop your image here' : 'Drag & drop an image'}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              or click to browse (PNG, JPG, WebP)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
