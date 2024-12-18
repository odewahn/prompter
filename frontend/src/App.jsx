import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  TextField,
  Button,
} from "@mui/material";
import AceEditor from "react-ace";
import { ThemeProvider } from "@mui/material/styles";
import nightModeTheme from "./theme";
import "./App.css";
import PromptWorkshop from "./PromptWorkshop";
import GroupSelector from "./GroupSelector";

function App() {
  const [selectedBlockContent, setSelectedBlockContent] = useState("");

  const handleGroupSelect = (group) => {
    console.log("Selected group:", group);
  };

  const handleBlockSelect = (block) => {
    setSelectedBlockContent(block);
  };

  const SelectedBlock = ({ block }) => (
    <div className="block-content">
      {block ? (
        <AceEditor
          mode="text"
          theme="github"
          name="blockContentEditor"
          value={block.content}
          readOnly={true}
          fontSize={16}
          style={{ height: "1000px" }}
          minLines={50}
          setOptions={{
            useWorker: false,
            showLineNumbers: true,
            showGutter: true,
            tabSize: 2,
            wrap: true,
            showPrintMargin: false,
          }}
        />
      ) : (
        <Typography>Select a block to view its content</Typography>
      )}
    </div>
  );

  const CommandInput = () => {
    const [command, setCommand] = useState("");

    const handleCommandSubmit = async (e) => {
      if (e.key !== "Enter") return;
      try {
        const response = await fetch("http://localhost:8000/api/command", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ command: encodeURIComponent(command) }),
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }

        const result = await response.json();
        console.log("Command result:", result);
        setCommand(""); // Clear the command input after submission
      } catch (error) {
        console.error("Failed to execute command:", error);
      }
    };

    return (
      <div className="command-input-div">
        <TextField
          label="Enter Command"
          variant="outlined"
          fullWidth
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleCommandSubmit}
        />
      </div>
    );
  };

  return (
    <ThemeProvider theme={nightModeTheme}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div">
            Prompter
          </Typography>
        </Toolbar>
      </AppBar>
      <Container className="app-container" maxWidth={false}>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={12} md={12} lg={12}>
            <CommandInput />
          </Grid>
          <Grid item xs={12} sm={4} md={4} lg={4}>
            <GroupSelector
              onGroupSelect={handleGroupSelect}
              onBlockSelect={handleBlockSelect}
            />
          </Grid>
          <Grid item xs={12} sm={8} md={8} lg={8}>
            <PromptWorkshop block={selectedBlockContent} />
            <SelectedBlock block={selectedBlockContent} />
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;
