import os
from jinja2 import Environment, FileSystemLoader

class Templator:
    def __init__(self, folder: str = "templates"):
        
        self.env = Environment()
        # Define the base directory of the project
        self.base_dir = os.getcwd()
        # Set the loader to the templates folder within the my_app directory
        self.env.loader = FileSystemLoader(os.path.join(self.base_dir, folder))
        
    def render(self, template_name: str, content: dict = {}, **kwargs):
        """
        Render a template with the given context.

        :param template_name: Name of the template file to render.
        :param content: Context data to pass to the template.
        :param folder: Folder where the template is located.
        :param kwargs: Context variables to pass to the template.
        :return: Rendered HTML as a string.
        """
        # Load the template 
        template = self.env.get_template(template_name)
        content = content or {}
        if not isinstance(content, dict):
            raise TypeError("Content must be a dictionary.")
        # Render the template with the provided context
        return template.render(content, **kwargs)