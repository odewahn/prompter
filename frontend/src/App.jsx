import React, { useState, useEffect } from "react";
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Paper, 
  Card, 
  CardContent, 
  Button 
} from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import nightModeTheme from "./theme";
import "./App.css";

function App() {
  const [currentGroupIndex, setCurrentGroupIndex] = useState(0);
  const [blockContents, setBlockContents] = useState([]);
  const [selectedBlockContent, setSelectedBlockContent] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/blocks")
      .then((response) => response.json())
      .then((data) => {
        setData(data);
        if (data.blocks) {
          const contents = data.blocks.map((block) => block.content);
          setBlockContents(contents);
        }
      })
      .catch((error) => console.error("Error fetching data:", error));

    fetch("http://localhost:8000/api/groups")
      .then((response) => response.json())
      .then((groupsData) => setGroups(groupsData))
      .catch((error) => console.error("Error fetching groups:", error));
  }, []);

  const handleNextGroup = () => {
    setCurrentGroupIndex((prevIndex) => (prevIndex + 1) % groups.length);
  };

  const handlePreviousGroup = () => {
    setCurrentGroupIndex((prevIndex) => (prevIndex - 1 + groups.length) % groups.length);
  };

  useEffect(() => {
    if (groups.length > 0) {
      const currentGroup = groups[currentGroupIndex];
      fetch(`http://localhost:8000/api/blocks/${currentGroup.tag}`)
        .then((response) => response.json())
        .then((data) => {
          setData(data);
          if (data.blocks) {
            const contents = data.blocks.map((block) => block.content);
            setBlockContents(contents);
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
        <Paper className="groups-column" elevation={3}>
          <Typography variant="h6">Groups</Typography>
          {groups.length > 0 && (
            <Card variant="outlined" style={{ marginBottom: "10px" }}>
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
          <Button onClick={handlePreviousGroup} disabled={groups.length === 0}>
            Previous
          </Button>
          <Button onClick={handleNextGroup} disabled={groups.length === 0}>
            Next
          </Button>
          <Typography variant="h6">Blocks</Typography>
          {blockContents.map((content, index) => (
            <Card
              key={index}
              variant="outlined"
              style={{ marginBottom: "10px", cursor: "pointer" }}
              onClick={() => setSelectedBlockContent(content)}
            >
              <CardContent>
                <Typography variant="body2" color="textSecondary" component="p">
                  {content.slice(0, 40)}...
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Paper>

        <Paper className="blocks-column" elevation={3}>
          <Typography variant="h6">Block Content</Typography>
          {selectedBlockContent ? (
            <Typography variant="body2" color="textSecondary" component="p">
              {selectedBlockContent}
            </Typography>
          ) : (
            <Typography>Select a block to view its content</Typography>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;
