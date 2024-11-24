import React, { useState, useEffect } from "react";

import AceEditor from "react-ace";
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/ext-language_tools"; // Import language tools for autocompletion
import "ace-builds/src-noconflict/theme-github";

export default function FileEditor({ value, language, onChange }) {
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        onChange(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".txt,.md,.html,.js,.json,.py,.java,.c,.cpp,.cs,.rb,.go,.rs,.ts,.tsx"
        onChange={handleFileChange}
        style={{ marginBottom: "10px" }}
      />
    <AceEditor
      mode={language} // Use the language prop for mode
      theme="github"
      name="editor"
      value={value}
      onChange={onChange}
      fontSize={14}
      width="100%"
      setOptions={{
        enableBasicAutocompletion: true,
        enableLiveAutocompletion: true,
        enableSnippets: true,
        showLineNumbers: true,
        tabSize: 2,
        useWorker: false, // Disable the worker to avoid issues with custom modes
        wrap: true, // Enable line wrapping
      }}
    />
    </div>
  );
}
