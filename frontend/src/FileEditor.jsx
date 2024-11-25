import React, { useState, useEffect } from "react";

import { IconButton } from "@mui/material";
import { Save, FolderOpen } from "@mui/icons-material";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/theme-eclipse";
import "ace-builds/src-noconflict/mode-handlebars";
import "ace-builds/src-noconflict/mode-yaml";

import "./FileEditor.css";

function FileEditor({ value, language, onChange }) {
  const [filename, setFilename] = useState("edited-file.txt");
  const [mode, setMode] = useState("jinja2");

  useEffect(() => {
    if (language === "yaml") {
      setMode("yaml");
    } else {
      setMode("handlebars");
    }
  }, [language]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFilename(file.name); // Store the filename
      console.log(file.name);
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
      <div className="button-column">
        <input
          type="file"
          accept=".txt,.md,.yaml,.jinja2,.jinja"
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="file-input"
        />
        <label htmlFor="file-input">
          <IconButton component="span">
            <FolderOpen />
          </IconButton>
        </label>
        <IconButton onClick={handleSave}>
          <Save />
        </IconButton>
      </div>
      <div className="editor-wrapper">
        <AceEditor
          mode={mode} // Use the language prop for mode
          height="250px"
          theme="eclipse"
          name="editor"
          value={value}
          onChange={(newValue) => {
            onChange(newValue);
          }}
          fontSize={16}
          width="100%"
          setOptions={{
            showLineNumbers: true,
            tabSize: 2,
            useWorker: false, // Disable the worker to avoid issues with custom modes
            wrap: true, // Enable line wrapping
            maxPixelHeight: 400,
            indentedSoftWrap: false,
          }}
        />
      </div>

    </div>
  );
}

export default FileEditor;
