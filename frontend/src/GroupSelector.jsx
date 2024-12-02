import React, { useState, useEffect } from "react";
import "./GroupSelector.css";
import {
  Grid,
  Card,
  CardContent,
  IconButton,
  Typography,
  Popover,
} from "@mui/material";
import { ArrowBack, ArrowForward, Info } from "@mui/icons-material";

function GroupSelector({ onGroupSelect, onBlockSelect }) {
  const [currentGroupIndex, setCurrentGroupIndex] = useState(-1);
  const [groups, setGroups] = useState([]);
  const [blockContents, setBlockContents] = useState([]);
  const [selectedBlockContent, setSelectedBlockContent] = useState({});
  const [anchorEl, setAnchorEl] = useState(null);

  useEffect(() => {
    const fetchGroups = () => {
      fetch("http://localhost:8000/api/groups")
        .then((response) => response.json())
        .then((groupsData) => {
          setGroups(groupsData);
          const currentGroupIndex = groupsData.findIndex(
            (group) => group.is_current === 1
          );
          if (currentGroupIndex !== -1) {
            setCurrentGroupIndex(currentGroupIndex);
          }
        })
        .catch((error) => console.error("Error fetching groups:", error));
    };

    fetchGroups();
    const intervalId = setInterval(fetchGroups, 500);

    return () => clearInterval(intervalId);
  }, []);

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
              onBlockSelect(data.blocks[0]);
            } else {
              setSelectedBlockContent({});
            }
          }
        })
        .catch((error) => console.error("Error fetching blocks:", error));
    }
  }, [currentGroupIndex]);

  const handlePopoverOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handlePopoverClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  const setCurrentGroup = async (tag) => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/set-current-group",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ tag }),
        }
      );

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Failed to set current group:", error);
    }
  };

  const handleNextGroup = () => {
    setCurrentGroupIndex((prevIndex) => {
      const newIndex = Math.min(prevIndex + 1, groups.length - 1);
      setCurrentGroup(groups[newIndex].tag);
      onGroupSelect(groups[newIndex]);
      return newIndex;
    });
  };

  const handlePreviousGroup = () => {
    setCurrentGroupIndex((prevIndex) => {
      const newIndex = Math.max(prevIndex - 1, 0);
      setCurrentGroup(groups[newIndex].tag);
      onGroupSelect(groups[newIndex]);
      return newIndex;
    });
  };

  return (
    <Grid item xs={12} sm={4} md={4} lg={4}>
      <div className="groups-column">
        <div className="group-navigation">
          <IconButton
            onClick={handlePreviousGroup}
            disabled={currentGroupIndex <= 0}
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
            disabled={
              currentGroupIndex === -1 || currentGroupIndex === groups.length - 1
            }
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
              onClick={() => {
                setSelectedBlockContent(block);
                onBlockSelect(block);
              }}
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
  );
}

export default GroupSelector;
