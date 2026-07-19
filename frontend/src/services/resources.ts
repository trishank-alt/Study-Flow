import api from './api';
import type { Resource } from '../types';

export const resourcesService = {
  async list(): Promise<Resource[]> {
    const { data } = await api.get<Resource[]>('/resources');
    return data;
  },

  async upload(
    file: File,
    title: string,
    subjectId?: number,
    topicId?: number
  ): Promise<Resource> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (subjectId !== undefined && subjectId !== null) {
      formData.append('subject_id', subjectId.toString());
    }
    if (topicId !== undefined && topicId !== null) {
      formData.append('topic_id', topicId.toString());
    }

    const { data } = await api.post<{ message: string; resource: Resource }>(
      '/resources',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data.resource;
  },

  async remove(id: number): Promise<void> {
    await api.delete(`/resources/${id}`);
  },
};
