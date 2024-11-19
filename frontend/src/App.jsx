import React, { useState, useEffect } from "react";

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
    <div style={{ display: "flex" }}>
      <div style={{ flex: 1, padding: "10px" }}>
        <h1>Groups</h1>
        <ul>
          {groups.map((group) => (
            <li key={group.id}>
              <a href="#" onClick={() => fetchBlocksForGroup(group.tag)}>
                {group.tag} - {group.command}
              </a>
            </li>
          ))}
        </ul>
      </div>

      <div style={{ flex: 2, padding: "10px" }}>
        <h1>Blocks Data</h1>
        {data ? (
          <div>
            <h2>Block Contents</h2>
            <ul>
              {blockContents.map((content, index) => (
                <li key={index}>{content}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p>Loading...</p>
        )}
      </div>
    </div>
  );
}

export default App;
