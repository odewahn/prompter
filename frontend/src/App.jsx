import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid2 as Grid,
  Paper,
} from "@mui/material";
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

  return (
    <ThemeProvider theme={nightModeTheme}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div">
            Prompter
          </Typography>
        </Toolbar>
      </AppBar>
      <Container className="app-container">
        <Grid container spacing={3}>
          <Grid item container xs={12} sm={4} md={4} lg={4}>
            <GroupSelector
              onGroupSelect={handleGroupSelect}
              onBlockSelect={handleBlockSelect}
            />
          </Grid>
          <Grid item container xs={12} sm={8} md={8} lg={8} direction="column">
            <PromptWorkshop block={selectedBlockContent} />
            <Paper className="blocks-column" elevation={3}>
              <Typography variant="h6">{selectedBlockContent.tag}</Typography>
              <hr />
              <div style={{ flex: 1, overflowY: "auto" }}>
                {selectedBlockContent ? (
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    component="pre"
                  >
                    {selectedBlockContent.content}
                  </Typography>
                ) : (
                  <Typography>Select a block to view its content</Typography>
                )}
              </div>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;
