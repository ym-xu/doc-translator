import React, { useState } from 'react';

function TranslationControls({ onTranslate, file, disabled }) {
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('zh');

  const handleTranslate = () => {
    onTranslate(file, sourceLanguage, targetLanguage);
  };

  return (
    <div className="translation-controls-container">
      <div className="language-selectors">
        <div className="language-select-group">
          <label>Source Language:</label>
          <select 
            value={sourceLanguage}
            onChange={(e) => setSourceLanguage(e.target.value)}
            className="language-select"
            disabled={disabled}
          >
            <option value="en">English</option>
            <option value="zh">中文</option>
            <option value="ja">日本語</option>
          </select>
        </div>
        
        <div className="language-select-group">
          <label>Target Language:</label>
          <select 
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
            className="language-select"
            disabled={disabled}
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
          </select>
        </div>

        <button 
          onClick={handleTranslate}
          className="translate-button"
          disabled={disabled}
        >
          {disabled ? 'Translating...' : 'Translate'}
        </button>
      </div>
    </div>
  );
}

export default TranslationControls;