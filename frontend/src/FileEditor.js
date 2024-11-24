import React, { useState, useEffect } from "react";

import AceEditor from "react-ace";
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/ext-language_tools"; // Import language tools for autocompletion
import "ace-builds/src-noconflict/theme-github";

function FileEditor({ value, language, onChange }) {
  return (
    <AceEditor
      mode="markdown" // Use markdown mode for better text handling
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
  );
}

export default function FileEditor({ value, language, onChange }) {
  return (
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
  );
}
