from jinja2 import Environment, BaseLoader, DebugUndefined

# https://stackoverflow.com/questions/28692549/keep-undefined-variables

template = """
prompt {{env.task_source}}/summarize.md --where "tag='{{block_tag[0]}}'"
"""

rtemplate = Environment(loader=BaseLoader, undefined=DebugUndefined).from_string(
    template
)

env = {"env": {"task_source": "https://example.com"}}

print(rtemplate.render(env))
