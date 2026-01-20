'use client';

import { useRouter } from 'next/navigation';
import UploadForm from '@/components/UploadForm';

export default function UploadPage() {
  const router = useRouter();

  const handleSuccess = (episodeId: number) => {
    router.push(`/episodes/${episodeId}`);
  };

  const handleCancel = () => {
    router.push('/');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <UploadForm onSuccess={handleSuccess} onCancel={handleCancel} />
    </div>
  );
}
