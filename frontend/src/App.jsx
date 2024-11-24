import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  IconButton,
  Popover,
  Paper,
} from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import nightModeTheme from "./theme";
import { ArrowBack, ArrowForward, Info } from "@mui/icons-material";
import "./App.css";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-html";
import "ace-builds/src-noconflict/theme-github";

function EditorComponent({ value, language, onChange }) {
  return (
    <AceEditor
      mode="html"
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
      }}
    />
  );
}

function App() {
  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);
  const [groups, setGroups] = useState([]);
  const [blockContents, setBlockContents] = useState([]);
  const [selectedBlockContent, setSelectedBlockContent] = useState("");
  const [taskPrompt, setTaskPrompt] = useState(
    groups[currentGroupIndex]?.task_prompt || ""
  );

  useEffect(() => {
    fetch("http://localhost:8000/api/groups")
      .then((response) => response.json())
      .then((groupsData) => {
        setGroups(groupsData);
        // find the index of the group where is_current = 1
        const currentGroupIndex = groupsData.findIndex(
          (group) => group.is_current === 1
        );
        if (currentGroupIndex !== -1) {
          setCurrentGroupIndex(currentGroupIndex);
          console.log(groupsData[currentGroupIndex]);
        }
      })
      .catch((error) => console.error("Error fetching groups:", error));
  }, []);

  useEffect(() => {
    if (groups.length > 0) {
      setTaskPrompt(groups[currentGroupIndex]?.task_prompt || "");
      const currentGroup = groups[currentGroupIndex];
      fetch(`http://localhost:8000/api/blocks/${currentGroup.tag}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.blocks) {
            setBlockContents(data.blocks);
            if (data.blocks.length > 0) {
              setSelectedBlockContent(data.blocks[0]);
            } else {
              setSelectedBlockContent({});
            }
          }
        })
        .catch((error) => console.error("Error fetching blocks:", error));
    }
  }, [currentGroupIndex]);

  const [anchorEl, setAnchorEl] = useState(null);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  const handleNextGroup = () => {
    setCurrentGroupIndex((prevIndex) =>
      Math.min(prevIndex + 1, groups.length - 1)
    );
  };

  const handlePreviousGroup = () => {
    setCurrentGroupIndex((prevIndex) => Math.max(prevIndex - 1, 0));
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
          <Grid item xs={12} sm={4} md={4} lg={4}>
            <div className="groups-column">
              <div className="group-navigation">
                <IconButton
                  onClick={handlePreviousGroup}
                  disabled={currentGroupIndex === 0}
                >
                  <ArrowBack />
                </IconButton>
                {groups.length > 0 && (
                  <Card
                    style={{
                      marginBottom: "10px",
                      flexGrow: 1,
                      minWidth: "20%",
                    }}
                    elevation={0}
                  >
                    <CardContent>
                      <div style={{ display: "flex", alignItems: "center" }}>
                        <Typography variant="subtitle2" color="textSecondary">
                          Group {currentGroupIndex + 1} of {groups.length}
                        </Typography>
                      </div>
                      <Typography variant="body1">
                        <IconButton
                          size="small"
                          onClick={handlePopoverOpen}
                          style={{ marginRight: "5px" }}
                        >
                          <Info fontSize="small" />
                        </IconButton>
                        {groups[currentGroupIndex].tag}
                      </Typography>
                    </CardContent>
                  </Card>
                )}
                <IconButton
                  onClick={handleNextGroup}
                  disabled={currentGroupIndex === groups.length - 1}
                >
                  <ArrowForward />
                </IconButton>
              </div>

              <div className="blocks-list">
                {blockContents.map((block, index) => (
                  <Card
                    key={index}
                    variant="outlined"
                    style={{
                      marginBottom: "10px",
                      cursor: "pointer",
                      backgroundColor:
                        selectedBlockContent === block ? "#f0f0f0" : "inherit",
                    }}
                    onClick={() => setSelectedBlockContent(block)}
                  >
                    <CardContent>
                      <Typography variant="subtitle2" color="textSecondary">
                        {block.tag}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {block.content ? block.content.slice(0, 30) : ""}...
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </div>
              <div className="block-count">
                <Typography variant="body2" color="textSecondary">
                  Block {blockContents.indexOf(selectedBlockContent) + 1} of{" "}
                  {blockContents.length}
                </Typography>
              </div>
              <Popover
                open={open}
                anchorEl={anchorEl}
                onClose={handlePopoverClose}
                anchorOrigin={{
                  vertical: "bottom",
                  horizontal: "left",
                }}
                transformOrigin={{
                  vertical: "top",
                  horizontal: "left",
                }}
              >
                <Typography sx={{ p: 2 }}>
                  {groups[currentGroupIndex]?.command || "No command available"}
                </Typography>
              </Popover>
            </div>
          </Grid>
          <Grid item xs={12} sm={8} md={8} lg={8}>
            <Paper className="blocks-column" elevation={3}>
              <EditorComponent
                value={groups[currentGroupIndex]?.task_prompt || ""}
                language="jinja"
                onChange={(value) => {
                  setTaskPrompt(value);
                  const updatedGroups = [...groups];
                  updatedGroups[currentGroupIndex].task_prompt = value;
                  setGroups(updatedGroups);
                }}
              />
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
