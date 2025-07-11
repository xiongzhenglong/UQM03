import React from 'react';
import Editor from '@monaco-editor/react';

interface SimpleCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
}

const SimpleCodeEditor: React.FC<SimpleCodeEditorProps> = ({
  value,
  onChange,
  language = 'javascript',
  height = '400px'
}) => {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(value) => onChange(value || '')}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          formatOnPaste: true,
          automaticLayout: true,
          readOnly: false,
        }}
        theme="vs-dark"
      />
    </div>
  );
};

export default SimpleCodeEditor; 