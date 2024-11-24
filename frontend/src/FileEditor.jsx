import React, { useState } from "react";

import { Button } from "@mui/material";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/ext-language_tools"; // Import language tools for autocompletion
import "ace-builds/src-noconflict/theme-github";

//import "./FileEditor.css";

function FileEditor({ value, language, onChange }) {
  const [filename, setFilename] = useState("edited-file.txt");

  console.log("GOT HERE");

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFilename(file.name); // Store the filename
      const reader = new FileReader();
      reader.onload = (e) => {
        onChange(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleSave = () => {
    const blob = new Blob([value], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename; // Use the stored filename
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="file-editor-container">
      <input
        type="file"
        accept=".txt,.md,.yaml,.jinja2,.jinja"
        onChange={handleFileChange}
        style={{ display: "none" }}
        id="file-input"
      />
      <label htmlFor="file-input">
        <Button
          variant="contained"
          component="span"
          style={{ marginBottom: "10px" }}
        >
          Select File
        </Button>
      </label>
      <Button
        variant="contained"
        onClick={handleSave}
        style={{ marginBottom: "10px", marginRight: "10px" }}
      >
        Save
      </Button>
      <AceEditor
        mode={language} // Use the language prop for mode
        theme="github"
        name="editor"
        value={value}
        onChange={(newValue) => {
          onChange(newValue);
        }}
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

export default FileEditor;
