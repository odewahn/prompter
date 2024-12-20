import React, { useState, useEffect } from "react";

import { IconButton } from "@mui/material";
import { Save, FolderOpen } from "@mui/icons-material";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/ace";
import "ace-builds/src-noconflict/theme-eclipse";
import "ace-builds/src-noconflict/mode-handlebars";
import "ace-builds/src-noconflict/mode-yaml";

import "./FileEditor.css";

function FileEditor({ filename, value, language, onChange, onFilenameChange }) {
  const [mode, setMode] = useState("handlebars");

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
      onFilenameChange(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        onChange(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleSave = () => {
    if (window.showSaveFilePicker) {
      const options = {
        suggestedName: filename,
        types: [
          {
            description: "Text Files",
            accept: {
              "text/plain": [".txt", ".md", ".yaml", ".jinja2", ".jinja"],
            },
          },
        ],
      };

      window
        .showSaveFilePicker(options)
        .then((fileHandle) => {
          fileHandle.createWritable().then((writable) => {
            writable.write(value).then(() => {
              writable.close();
              onFilenameChange(fileHandle.name);
            });
          });
        })
        .catch((error) => {
          console.error("Save operation failed:", error);
        });
    } else {
      // Fallback for browsers that do not support showSaveFilePicker
      const blob = new Blob([value], { type: "text/plain;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
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
        {filename}
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
