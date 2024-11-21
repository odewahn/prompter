import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Paper,
  Card,
  CardContent,
  Button,
  IconButton,
  LinearProgress,
} from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import nightModeTheme from "./theme";
import { ArrowBack, ArrowForward } from "@mui/icons-material";
import "./App.css";

function App() {
  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);
  const [groups, setGroups] = useState([]);
  const [blockContents, setBlockContents] = useState([]);
  const [selectedBlockContent, setSelectedBlockContent] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/blocks")
      .then((response) => response.json())
      .then((data) => {
        if (data.blocks) {
          setBlockContents(data.blocks);
        }
      })
      .catch((error) => console.error("Error fetching data:", error));

    fetch("http://localhost:8000/api/groups")
      .then((response) => response.json())
      .then((groupsData) => setGroups(groupsData))
      .catch((error) => console.error("Error fetching groups:", error));
  }, []);

  const handleNextGroup = () => {
    setCurrentGroupIndex((prevIndex) =>
      Math.min(prevIndex + 1, groups.length - 1)
    );
  };

  const handlePreviousGroup = () => {
    setCurrentGroupIndex((prevIndex) => Math.max(prevIndex - 1, 0));
  };

  useEffect(() => {
    if (groups.length > 0) {
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
  }, [currentGroupIndex, groups]);

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
                style={{ marginBottom: "10px", flexGrow: 1, minWidth: "20%" }}
                elevation={0}
              >
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary">
                    {groups[currentGroupIndex].tag}
                  </Typography>
                  <Typography variant="body1">
                    {groups[currentGroupIndex].command}
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
          <LinearProgress
            variant="determinate"
            value={(currentGroupIndex / (groups.length - 1)) * 100}
            style={{ width: "100%", marginTop: "10px" }}
          />
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
        </div>

        <Paper className="blocks-column" elevation={3}>
          {selectedBlockContent ? (
            <div>
              <Typography variant="h6">{selectedBlockContent.tag}</Typography>
              <Typography variant="body2" color="textSecondary" component="pre">
                {selectedBlockContent.content}
              </Typography>
            </div>
          ) : (
            <Typography>Select a block to view its content</Typography>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;
