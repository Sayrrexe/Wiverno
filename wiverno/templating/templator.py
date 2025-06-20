import os
from jinja2 import Environment, FileSystemLoader

def render(template_name: str, content: dict = {}, folder: str = "templates", **kwargs):
    """
    Render a template with the given context.
    
    :param template_name: Name of the template file to render.
    :param content: Context data to pass to the template.
    :param folder: Folder where the template is located.
    :param kwargs: Context variables to pass to the template.
    :return: Rendered HTML as a string.
    """
    env = Environment()
    
    # Define the base directory of the project
    base_dir = os.getcwd()

    # Set the loader to the templates folder within the my_app directory
    env.loader = FileSystemLoader(os.path.join(base_dir, folder))
    
    # Load the template 
    template = env.get_template(template_name)
    # Check if the template exists
    if not template:
        raise FileNotFoundError(f"Template '{template_name}' not found in folder '{folder}'.")
    
    if content != {}:
        # Ensure content is a dictionary
        if not isinstance(content, dict):
            raise TypeError("Content must be a dictionary.")
    
    # Render the template with the provided context
    return template.render(content, **kwargs)