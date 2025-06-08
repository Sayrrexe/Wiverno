import os
from jinja2 import Template

def render(template_name, folder="templates", **kwargs):
    """
    Render a template with the given context.
    
    :param template_name: Name of the template file to render.
    :param folder: Folder where the template is located.
    :param kwargs: Context variables to pass to the template.
    :return: Rendered HTML as a string.
    """
    # Определяем базовую директорию проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construct the full path to the template file
    template_path = os.path.join(base_dir, 'my_app', folder, template_name)
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()
    
    # Create a Jinja2 Template object
    template = Template(template_content)
    
    # Render the template with the provided context
    return template.render(**kwargs)