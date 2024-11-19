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
          const contents = data.blocks.map(block => block.content);
          setBlockContents(contents);
        }
      })
      .catch((error) => console.error("Error fetching data:", error));
    fetch("http://localhost:8000/api/groups")
      .then((response) => response.json())
      .then((groupsData) => setGroups(groupsData))
      .catch((error) => console.error("Error fetching groups:", error));
  }, []);

  const fetchBlocksForGroup = (blockTag) => {
    fetch(`http://localhost:8000/api/blocks/${blockTag}`)
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
    <div>
      <h1>Groups</h1>
      <ul>
        {groups.map((group) => (
          <li key={group.id}>
            <a href="#" onClick={() => fetchBlocksForGroup(group.group_tag)}>
              {group.group_tag} - {group.command}
            </a>
          </li>
        ))}
      </ul>

      <h1>Blocks Data</h1>
      {data ? (
        <div>
          <h2>Block Contents</h2>
          <ul>
            {blockContents.map((content, index) => (
              <li key={index}>{content}</li>
            ))}
          </ul>
          <h2>Full Data</h2>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default App;
