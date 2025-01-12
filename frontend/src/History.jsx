import React, { useState, useEffect } from "react";
import { IconButton, Typography, Box } from "@mui/material";
import { ArrowDropDown, ArrowRight } from "@mui/icons-material";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-text";
import "ace-builds/src-noconflict/theme-github";

function History() {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [commandHistory, setCommandHistory] = useState("");

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  useEffect(() => {
    const fetchCommandHistory = () => {
      fetch("http://localhost:8000/api/groups")
        .then((response) => response.json())
        .then((groupsData) => {
          const commands = groupsData.map((group) => group.command).join("\n");
          setCommandHistory(commands);
        })
        .catch((error) =>
          console.error("Error fetching command history:", error)
        );
    };

    fetchCommandHistory();
    const intervalId = setInterval(fetchCommandHistory, 500);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="history-container">
      <IconButton
        disableRipple
        onClick={toggleCollapse}
        style={{ marginBottom: "10px" }}
      >
        {isCollapsed ? <ArrowRight /> : <ArrowDropDown />}
        <Typography variant="button" style={{ marginLeft: "5px" }}>
          History
        </Typography>
      </IconButton>
      {!isCollapsed && (
        <Box sx={{ p: 3 }}>
          <AceEditor
            mode="text"
            theme="github"
            name="historyEditor"
            value={commandHistory}
            readOnly={true}
            width="100%"
            height="200px"
            fontSize={16}
            setOptions={{
              useWorker: false,
              showLineNumbers: true,
              showGutter: true,
              tabSize: 2,
              wrap: true,
              showPrintMargin: false,
            }}
          />
        </Box>
      )}
    </div>
  );
}

export default History;
