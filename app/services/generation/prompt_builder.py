# app/services/generation/prompt_builder.py

from jinja2 import Template

class PromptBuilder:
    def __init__(self, template_str: str):
        self.template = Template(template_str)

    def render(self, **kwargs) -> str:
        # kwargs can include: name, lat, lon, description, topic, style, etc.
        return self.template.render(**kwargs)
