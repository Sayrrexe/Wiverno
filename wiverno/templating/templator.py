from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class Templator:
    def __init__(self, folder: str = "templates"):

        self.env = Environment()
        # Base directory of the framework package
        self.base_dir = Path(__file__).resolve().parent
        # Load templates from the provided folder relative to the package
        self.env.loader = FileSystemLoader(self.base_dir / folder)
        
    def render(self, template_name: str, content: dict = {}, **kwargs):
        """
        Render a template with the given context.

        :param template_name: Name of the template file to render.
        :param content: Context data to pass to the template.
        :param kwargs: Additional context variables.
        :return: Rendered HTML as a string.
        """
        # Load the template 
        template = self.env.get_template(template_name)
        content = content or {}
        if not isinstance(content, dict):
            raise TypeError("Content must be a dictionary.")
        # Render the template with the provided context
        return template.render(content, **kwargs)