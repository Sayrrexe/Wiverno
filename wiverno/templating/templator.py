import os

from jinja2 import Environment, FileSystemLoader


class Templator:
    """
    Template rendering wrapper around Jinja2.

    Provides a simple interface for loading and rendering Jinja2 templates
    from a specified folder.
    """

    def __init__(self, folder: str = "templates"):
        """
        Initializes the Templator with a template folder.

        Args:
            folder (str, optional): Path to the templates folder relative to
                the current working directory. Defaults to "templates".
        """

        self.env = Environment()
        self.base_dir = os.getcwd()
        self.env.loader = FileSystemLoader(os.path.join(self.base_dir, folder))

    def render(self, template_name: str, content: dict | None = None, **kwargs):
        """
        Renders a template with the given context.

        Args:
            template_name (str): Name of the template file to render.
            content (Optional[dict]): Context data to pass to the template. Defaults to None.
            **kwargs: Additional context variables to pass to the template.

        Returns:
            str: Rendered HTML as a string.

        Raises:
            TypeError: If content is not a dictionary.
        """
        template = self.env.get_template(template_name)
        content = content or {}
        if not isinstance(content, dict):
            raise TypeError("Content must be a dictionary.")
        return template.render(**content, **kwargs)
