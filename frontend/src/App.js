import React, { useState } from 'react';
import Upload from './components/Upload';
import TranslationControls from './components/TranslationControls';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';
import './index.css'
import { Rocket, FileType, Shield, Upload as UploadIcon } from 'lucide-react'
import { Card, CardContent } from './components/ui/card';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [originalFile, setOriginalFile] = useState(null);
  const [translatedUrl, setTranslatedUrl] = useState(null);

  const handleFileSelect = (file) => {
    setOriginalFile(file);
  };

  const handleTranslate = async (file, sourceLanguage, targetLanguage) => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    setIsLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source_language', sourceLanguage);
      formData.append('target_language', targetLanguage);
      
      const response = await fetch('http://localhost:8000/api/translate', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Translation failed');
      }
      
      const data = await response.json();
      const jobId = data.jobId;
      console.log('Translation job created:', data);
      
      // 开始轮询任务状态
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(`http://localhost:8000/api/jobs/${jobId}`);
        const jobStatus = await statusResponse.json();
        console.log('Job status:', jobStatus);
        
        if (jobStatus.status === 'completed' && jobStatus.result_url) {
          clearInterval(pollInterval);
          console.log('Setting translated URL:', jobStatus.result_url);
          setTranslatedUrl(jobStatus.result_url);
          setIsLoading(false);
        } else if (jobStatus.status === 'failed') {
          clearInterval(pollInterval);
          setIsLoading(false);
          alert(`Translation failed: ${jobStatus.error || 'Unknown error'}`);
        }
      }, 2000);
      
    } catch (error) {
      console.error('Translation error:', error);
      alert('Failed to translate document');
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      {!originalFile ? (
        <div className="landing-page">
          <div className="landing-content">
            <header className="App-header">
              <h1>Doc Translator</h1>
              <p className="subtitle">Upload your PDF document and get it translated</p>
            </header>
            <main className="App-main">
              <div className="upload-section">
                <Upload onFileSelect={handleFileSelect} />
              </div>
              <div className="features">
              <FeatureCard
                icon={<Rocket className="h-8 w-8 mb-2 text-blue-500" />}
                title="Fast Translation"
                description="Quick and accurate document translation"
              />
              <FeatureCard
                icon={<FileType className="h-8 w-8 mb-2 text-green-500" />}
                title="Format Preserved"
                description="Maintains original PDF layout and styling"
              />
              <FeatureCard
                icon={<Shield className="h-8 w-8 mb-2 text-purple-500" />}
                title="Secure"
                description="Your documents are processed securely"
              />
              </div>
            </main>
          </div>
        </div>
      ) : (
        <div className="document-workspace">
          <PDFPreview file={originalFile} title="Original Document" isTranslated={false} />
          <div className="control-panel">
            {!translatedUrl ? (
              <div className="translation-controls-container">
                <TranslationControls 
                  onTranslate={handleTranslate}
                  file={originalFile}
                  disabled={isLoading}
                />
                {isLoading && <LoadingSpinner />}
              </div>
            ) : (
              <PDFPreview 
                file={translatedUrl} 
                title="Translated Document" 
                isTranslated={true} 
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function PDFPreview({ file, title, isTranslated }) {
  return (
    <div className="preview-panel">
      <div className="preview-header">
        <h3 className="text-lg font-medium">{title}</h3>
      </div>
      <div className="preview-content">
        <iframe
          src={typeof file === 'string' ? file : URL.createObjectURL(file)}
          title={title}
          className="pdf-frame"
        />
        {isTranslated && (
          <div className="preview-overlay">
            <div className="preview-message">
              Preview of first 2 pages only
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center text-center p-6">
        {icon}
        <h3 className="font-semibold text-lg mb-2">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </CardContent>
    </Card>
  )
}

export default App;
