create table if not exists block_groups (
    id integer primary key autoincrement,
    is_current boolean DEFAULT 0
    command text,
    tag text,
    created_at datetime DEFAULT CURRENT_TIMESTAMP
);

create table if not exists blocks (
    id integer primary key autoincrement,
    tag text,
    block_group_id int,   
    created_at datetime DEFAULT CURRENT_TIMESTAMP,
    block text,
    token_count int,
    CONSTRAINT fk_group
        FOREIGN KEY (block_group_id)
        REFERENCES block_groups(id)
        ON DELETE CASCADE,
);

create table if not exists completion_groups (
    id integer primary key autoincrement,
    prompt_fn text,
    persona_fn text,
    prompt text,
    command text,
    tag text,
    created_at datetime DEFAULT CURRENT_TIMESTAMP
);

create table if not exists completions (
    id integer primary key autoincrement,
    completion_group_id int,
    block_id int,
    response text,
    elapsed_time_in_seconds float,
    created_at datetime DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_completions_groups
        FOREIGN KEY (completion_group_id)
        REFERENCES complection_groups(id)
        ON DELETE CASCADE,
);




