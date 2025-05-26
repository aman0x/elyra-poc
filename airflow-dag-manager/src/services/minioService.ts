import AWS from 'aws-sdk';
import { MINIO_CONFIG } from '../utils/constants';
import { handleApiError } from '../utils/helpers';
import { MinioObject } from '../types/api';

class MinioService {
  private s3: AWS.S3;

  constructor() {
    // Configure AWS SDK to work with MinIO
    AWS.config.update({
      accessKeyId: MINIO_CONFIG.ACCESS_KEY,
      secretAccessKey: MINIO_CONFIG.SECRET_KEY,
      s3ForcePathStyle: true, // needed for MinIO
      signatureVersion: 'v4'
    });

    this.s3 = new AWS.S3({
      endpoint: `${MINIO_CONFIG.USE_SSL ? 'https' : 'http'}://${MINIO_CONFIG.ENDPOINT}`,
      s3ForcePathStyle: true,
      signatureVersion: 'v4'
    });
  }

  /**
   * List all objects in the DAG bucket
   */
  async listDagFiles(): Promise<MinioObject[]> {
    try {
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        MaxKeys: 1000
      };

      const response = await this.s3.listObjectsV2(params).promise();
      
      return (response.Contents || []).map(obj => ({
        name: obj.Key || '',
        lastModified: obj.LastModified || new Date(),
        etag: obj.ETag || '',
        size: obj.Size || 0
      }));
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Get DAG file content
   */
  async getDagFileContent(fileName: string): Promise<string> {
    try {
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Key: fileName
      };

      const response = await this.s3.getObject(params).promise();
      return response.Body?.toString('utf-8') || '';
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Get DAG files for a specific DAG (by prefix)
   */
  async getDagFiles(dagId: string): Promise<MinioObject[]> {
    try {
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Prefix: dagId,
        MaxKeys: 100
      };

      const response = await this.s3.listObjectsV2(params).promise();
      
      return (response.Contents || []).map(obj => ({
        name: obj.Key || '',
        lastModified: obj.LastModified || new Date(),
        etag: obj.ETag || '',
        size: obj.Size || 0
      }));
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Upload a file to MinIO bucket
   */
  async uploadFile(file: File, fileName?: string): Promise<string> {
    try {
      const key = fileName || file.name;
      
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Key: key,
        Body: file,
        ContentType: file.type || 'application/octet-stream'
      };

      const response = await this.s3.upload(params).promise();
      return response.Location || key;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Upload file with progress tracking
   */
  async uploadFileWithProgress(
    file: File, 
    fileName?: string,
    onProgress?: (progress: number) => void
  ): Promise<string> {
    try {
      const key = fileName || file.name;
      
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Key: key,
        Body: file,
        ContentType: file.type || 'application/octet-stream'
      };

      const upload = this.s3.upload(params);
      
      // Track upload progress
      if (onProgress) {
        upload.on('httpUploadProgress', (progress) => {
          const percentage = Math.round((progress.loaded / progress.total) * 100);
          onProgress(percentage);
        });
      }

      const response = await upload.promise();
      return response.Location || key;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Delete a file from MinIO bucket
   */
  async deleteFile(fileName: string): Promise<void> {
    try {
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Key: fileName
      };

      await this.s3.deleteObject(params).promise();
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Check if a file exists in the bucket
   */
  async fileExists(fileName: string): Promise<boolean> {
    try {
      const params = {
        Bucket: MINIO_CONFIG.BUCKET_NAME,
        Key: fileName
      };

      await this.s3.headObject(params).promise();
      return true;
    } catch (error: any) {
      if (error.statusCode === 404) {
        return false;
      }
      throw new Error(handleApiError(error));
    }
  }

  /**
   * Check if bucket exists and is accessible
   */
  async checkConnection(): Promise<boolean> {
    try {
      await this.s3.headBucket({ Bucket: MINIO_CONFIG.BUCKET_NAME }).promise();
      return true;
    } catch (error) {
      console.error('MinIO connection failed:', handleApiError(error));
      return false;
    }
  }
}

export const minioService = new MinioService();