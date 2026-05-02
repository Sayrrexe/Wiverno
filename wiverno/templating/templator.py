from pathlib import Path
from typing import Annotated

from annotated_doc import Doc
from jinja2 import Environment, FileSystemLoader


class Templator:
    """
    Template rendering wrapper around Jinja2.

    Provides a simple interface for loading and rendering Jinja2 templates
    from a specified folder.
    """

    def __init__(
        self,
        folder: Annotated[
            str | Path,
            Doc(
                """
                Path to the directory containing Jinja2 templates. Can be
                specified as a string (relative or absolute path) or as
                a Path object. Defaults to "templates" folder.
                """
            )] = "templates"
    ) -> None:
        """
        Initializes the Templator with a template folder.

        Args:
            folder (str | Path, optional): Path to the templates folder relative to
                the current working directory, or an absolute path.
                Can be a string or Path object. Defaults to "templates".
        """

        self.env = Environment(autoescape=True)
        self.base_dir = Path.cwd()

        folder_path = Path(folder) if isinstance(folder, str) else folder

        template_dir = folder_path if folder_path.is_absolute() else self.base_dir / folder_path

        self.env.loader = FileSystemLoader(str(template_dir))

    def render(
        self,
        template_name: str, content: dict[str, object] | None = None,
        **kwargs: object
    ) -> str:
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
        result: str = template.render(**content, **kwargs)
        return result
