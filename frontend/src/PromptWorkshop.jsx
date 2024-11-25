import React, { useState, useEffect } from "react";

import { Tabs, Tab, Box, Typography } from "@mui/material";
import "./PromptWorkshop.css";

import FileEditor from "./FileEditor.jsx";

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    "aria-controls": `simple-tabpanel-${index}`,
  };
}

export default function PromptWorkshop({ content, metadata }) {
  return (
    <div>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Task Prompt" {...a11yProps(0)} />
          <Tab label="Persona Prompt" {...a11yProps(1)} />
          <Tab label="Metadata" {...a11yProps(2)} />
          <Tab label="Model Settings" {...a11yProps(3)} />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <FileEditor
          value={taskPrompt}
          language="jinja"
          onChange={(value) => {
            setTaskPrompt(value);
          }}
        />
      </TabPanel>
      <TabPanel value={value} index={1}>
      <FileEditor
                value={taskPrompt}
                language="jinja"
                onChange={(value) => {
                  setTaskPrompt(value);
                }}
              />
      </TabPanel>
      <TabPanel value={value} index={2}>
      <FileEditor
                value={taskPrompt}
                language="jinja"
                onChange={(value) => {
                  setTaskPrompt(value);
                }}
              />
      </TabPanel>
      <TabPanel value={value} index={3}>
        Model Settings Content
      </TabPanel>
    </div>
  );
}
