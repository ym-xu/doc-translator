import React from 'react';

function TranslationViewer({ originalFile, translatedUrl }) {
  return (
    <div className="viewer-container">
      <div className="viewer-panel">
        <h3>Original Document</h3>
        <iframe
          src={URL.createObjectURL(originalFile)}
          title="Original PDF"
          className="pdf-frame"
        />
      </div>

      <div className="viewer-panel">
        <h3>Translated Document</h3>
        <iframe
          src={translatedUrl}
          title="Translated PDF"
          className="pdf-frame"
        />
      </div>
    </div>
  );
}

export default TranslationViewer;