# API

Prompter has a simple UI that is used to power the browser-based IDE. You can use it as a standalone tool to create and run scripts, or you can use it as a library to build your own tools.

This probably needs more endpoints, but it's a start.

## `/api/groups`

Get a list of all the groups in the database.

```json
[
  {
    "id": 1,
    "is_current": 0,
    "command": "load data/*.txt",
    "tag": "bbc-820",
    "created_at": "2025-02-14 15:14:04"
  },
  {
    "id": 2,
    "is_current": 1,
    "command": "transform new-line-split",
    "tag": "zec-572",
    "created_at": "2025-02-14 18:19:26"
  }
]
```

## `/api/blocks`

Fetch all the blocks in the current group:

```json
{
  "id": 2,
  "is_current": 1,
  "command": "transform new-line-split",
  "tag": "zec-572",
  "created_at": "2025-02-14 18:19:26",
  "blocks": [
    {
      "id": 3,
      "tag": "cat-essay.txt",
      "group_id": 2,
      "position": 0,
      "created_at": "2025-02-14 18:19:26",
      "content": "CATS ARE THE BEST.",
      "token_count": 4
    },
    {
      "id": 4,
      "tag": "cat-essay.txt",
      "group_id": 2,
      "position": 1,
      "created_at": "2025-02-14 18:19:26",
      "content": "Man's best friend has historically been considered a dog. But dogs are not the only animal friend whose camaraderie people enjoy. For many people, a cat is their best friend. Despite what dog lovers may believe, cats make excellent house pets because they are good companions, they are civilized members of the household, and they are easy to care for. Let me tell you why.",
      "token_count": 65
    },
    ...
    },
    {
      "id": 9,
      "tag": "dog-essay.txt",
      "group_id": 2,
      "position": 6,
      "created_at": "2025-02-14 18:19:26",
      "content": "Man's best friend has historically been considered a dog. But dogs are not the only animal friend whose camaraderie people enjoy. For many people, a dog is their best friend. Despite what dog lovers may believe, dogs make excellent house pets because they are good companions, they are civilized members of the household, and they are easy to care for. Let me tell you why.",
      "token_count": 65
    },
    ...
]
}
```

## `/api/blocks/:group_id`

Fetch the blocks for a specific group. For example, `/api/blocks/bbc-820`:

```json
{
  "id": 1,
  "is_current": 0,
  "command": "load data/*.txt",
  "tag": "bbc-820",
  "created_at": "2025-02-14 15:14:04",
  "blocks": [
    {
      "id": 1,
      "tag": "cat-essay.txt",
      "group_id": 1,
      "position": 1,
      "created_at": "2025-02-14 15:14:04",
      "content": "Man's best friend has historically been considered a dog. But dogs are not the only animal friend whose camaraderie people enjoy. For many people, a cat is their best friend. Despite what dog lovers may believe, cats make excellent house pets because they are good companions, they are civilized members of the household, and they are easy to care for. Let me tell you why....",
      "token_count": 362
    },
    {
      "id": 2,
      "tag": "dog-essay.txt",
      "group_id": 1,
      "position": 2,
      "created_at": "2025-02-14 15:14:04",
      "content": "Man's best friend has historically been considered a dog. But dogs are not the only animal friend whose camaraderie people enjoy. For many people, a dog is their best friend. Despite what dog lovers may believe, dogs make excellent house pets because they are good companions, they are civilized members of the household, and they are easy to care for. Let me tell you why....",
      "token_count": 358
    }
  ]
}
```
