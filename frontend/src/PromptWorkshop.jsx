import React, { useState, useEffect } from "react";

import {
  Tabs,
  Tab,
  Box,
  Typography,
  Button,
  CircularProgress,
  IconButton,
  Slider,
} from "@mui/material";
import { ArrowDropDown, ArrowRight } from "@mui/icons-material";
import "./PromptWorkshop.css";

import yaml from "js-yaml";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-text";
import "ace-builds/src-noconflict/theme-github";

import FileEditor from "./FileEditor.jsx";
import { set } from "ace-builds/src-noconflict/ace.js";

function TabPanel({ children, tabIndex, index, ...other }) {
  return (
    <div
      className="tab-container"
      role="tabpanel"
      hidden={tabIndex !== index}
      id={`simple-tabpanel-${index}`}
      {...other}
    >
      {tabIndex === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

export default function PromptWorkshop({ block }) {
  const [tabIndex, setTabIndex] = useState(0);
  const [isCollapsed, setIsCollapsed] = useState(true);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };
  const [taskPrompt, setTaskPrompt] = useState("");
  const [personaPrompt, setPersonaPrompt] = useState("");
  const [metadata, setMetadata] = useState("");
  const [model, setModel] = useState("gpt-4o-mini");
  const [temperature, setTemperature] = useState(0.1);
  const [completion, setCompletion] = useState("");
  const [waiting, setWaiting] = useState(false);

  const handleChange = (event, newTabIndex) => {
    setTabIndex(newTabIndex);
  };

  const convertYAMLtoJSON = (data) => {
    try {
      if (!data) {
        return {};
      }
      return yaml.load(data);
    } catch (e) {
      return {};
    }
  };

  const sendCompletionRequest = async (
    block,
    task,
    persona,
    metadata,
    model,
    temperature
  ) => {
    try {
      setWaiting(true);
      const response = await fetch("http://localhost:8000/api/complete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          block,
          task,
          persona,
          metadata,
          model,
          temperature,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const result = await response.json();
      setCompletion(result);
      setWaiting(false);
    } catch (error) {
      console.error("Failed to complete request:", error);
      setWaiting(false);
    }
  };

  return (
    <div className="prompt-workshop-container">
      <div>
        <IconButton
          disableRipple
          onClick={toggleCollapse}
          style={{ marginBottom: "10px" }}
        >
          {isCollapsed ? <ArrowRight /> : <ArrowDropDown />}
          <Typography variant="button" style={{ marginLeft: "5px" }}>
            Prompt Workshop
          </Typography>
        </IconButton>
        {!isCollapsed && (
          <>
            <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
              <Tabs
                value={tabIndex}
                onChange={handleChange}
                aria-label="basic tabs example"
                className="custom-tabs"
              >
                <Tab label="Task" />
                <Tab label="Persona" />
                <Tab label="Metadata" />
                <Tab label="Model" />
              </Tabs>
            </Box>
            <div>
              <TabPanel tabIndex={tabIndex} index={0}>
                <FileEditor
                  value={taskPrompt}
                  language="jinja"
                  onChange={(value) => {
                    setTaskPrompt(value);
                  }}
                />
              </TabPanel>
              <TabPanel tabIndex={tabIndex} index={1}>
                <FileEditor
                  value={personaPrompt}
                  language="jinja"
                  onChange={(value) => {
                    setPersonaPrompt(value);
                  }}
                />
              </TabPanel>
              <TabPanel tabIndex={tabIndex} index={2}>
                <FileEditor
                  value={metadata}
                  language="yaml"
                  onChange={(value) => {
                    setMetadata(value);
                  }}
                />
              </TabPanel>
            </div>
            <TabPanel tabIndex={tabIndex} index={3}>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                }}
              >
                <div>
                  <Typography variant="subtitle1">Model</Typography>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    style={{
                      width: "100%",
                      padding: "5px",
                      borderRadius: "4px",
                      border: "1px solid #ccc",
                    }}
                  />
                </div>
                <div>
                  <Typography variant="subtitle1">Temperature</Typography>
                  <Slider
                    value={temperature}
                    min={0}
                    max={1}
                    step={0.01}
                    onChange={(e, newValue) => setTemperature(newValue)}
                    valueLabelDisplay="auto"
                  />
                </div>
              </div>
            </TabPanel>
            <Button
              variant="contained"
              color="primary"
              onClick={() => {
                sendCompletionRequest(
                  block,
                  taskPrompt,
                  personaPrompt,
                  convertYAMLtoJSON(metadata),
                  model,
                  temperature
                );
              }}
              style={{ marginTop: "10px", marginBottom: "20px" }}
              disabled={waiting}
              startIcon={waiting ? <CircularProgress size={20} /> : null}
            >
              {waiting ? "Completing..." : "Complete"}
            </Button>
            <div>
              <AceEditor
                mode="text"
                theme="github"
                name="completionEditor"
                value={completion.completion}
                readOnly={true}
                width="100%"
                height="300px"
                fontSize={16}
                setOptions={{
                  useWorker: false,
                  showLineNumbers: false,
                  showGutter: false,
                  tabSize: 2,
                  wrap: true, // Enable line wrapping
                  indentedSoftWrap: false,
                }}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
