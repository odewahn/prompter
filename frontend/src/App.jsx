import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  List,
  ListItem,
  ListItemText,
  Paper,
  Card,
  CardContent,
} from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import nightModeTheme from "./theme";
import "./App.css";

function App() {
  const [data, setData] = useState(null);
  const [blockContents, setBlockContents] = useState([]);
  const [groups, setGroups] = useState([]);

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

  const fetchBlocksForGroup = (groupTag) => {
    fetch(`http://localhost:8000/api/blocks/${groupTag}`)
      .then((response) => response.json())
      .then((data) => {
        setData(data);
        if (data.blocks) {
          const contents = data.blocks.map((block) => block.content);
          setBlockContents(contents);
        }
      })
      .catch((error) => console.error("Error fetching blocks:", error));
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
        <Paper className="groups-column" elevation={3}>
          <Typography variant="h6">Groups</Typography>
          {groups.map((group) => (
            <Card
              key={group.id}
              variant="outlined"
              style={{ marginBottom: "10px" }}
              onClick={() => fetchBlocksForGroup(group.tag)}
              style={{ marginBottom: "10px", cursor: "pointer" }}
            >
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">
                  {group.tag}
                </Typography>
                <Typography variant="body1">{group.command}</Typography>
              </CardContent>
            </Card>
          ))}
        </Paper>

        <Paper className="blocks-column" elevation={3}>
          <Typography variant="h6">Blocks Data</Typography>
          {data ? (
            blockContents.map((content, index) => (
              <Card
                key={index}
                variant="outlined"
                style={{ marginBottom: "10px" }}
              >
                <CardContent>
                  <Typography
                    variant="body2"
                    color="textSecondary"
                    component="p"
                  >
                    {content}
                  </Typography>
                </CardContent>
              </Card>
            ))
          ) : (
            <Typography>Loading...</Typography>
          )}
        </Paper>
      </Container>
    </ThemeProvider>
  );
}

export default App;
