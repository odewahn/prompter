import React, { useState, useEffect } from "react";

import { Tabs, Tab, Box, Typography, Button } from "@mui/material";
import "./PromptWorkshop.css";

import FileEditor from "./FileEditor.jsx";

function TabPanel({ children, tabIndex, index, ...other }) {
  return (
    <div
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
  const [taskPrompt, setTaskPrompt] = useState("");
  const [personaPrompt, setPersonaPrompt] = useState("");
  const [metadata, setMetadata] = useState("");

  const handleChange = (event, newTabIndex) => {
    setTabIndex(newTabIndex);
  };

  return (
    <div>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={tabIndex}
          onChange={handleChange}
          aria-label="basic tabs example"
          sx={{
            "& .MuiTabs-indicator": {
              backgroundColor: "blue",
            },
            "& .Mui-selected": {
              outline: "none",
            },
          }}
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
      <Button
        variant="contained"
        color="primary"
        onClick={() => console.log(block)}
        style={{ marginTop: "10px" }}
      >
        Print Block
      </Button>
      <TabPanel tabIndex={tabIndex} index={3}>
        Model Settings Content
      </TabPanel>
    </div>
  );
}
