"""
Unit tests for Templator class.

Tests:
- Templator initialization
- Template rendering with context
- Error handling
- Jinja2 integration
"""

import os
from pathlib import Path

import pytest
from jinja2 import Environment, TemplateNotFound

from wiverno.templating.templator import Templator


# ============================================================================
# Templator Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestTemplatorInitialization:
    """Templator initialization tests."""

    def test_templator_default_folder(self):
        """Test: Templator should initialize with default folder."""
        templator = Templator()

        # Default folder is "templates"
        assert templator.env is not None
        assert isinstance(templator.env, Environment)

    def test_templator_custom_folder(self, temp_template_dir):
        """Test: Templator should accept custom folder."""
        templator = Templator(folder=str(temp_template_dir))

        assert templator.env is not None

    def test_templator_stores_base_dir(self):
        """Test: Templator should store base_dir."""
        templator = Templator()

        assert templator.base_dir == os.getcwd()
        assert isinstance(templator.base_dir, str)


# ============================================================================
# Template Rendering Tests
# ============================================================================


@pytest.mark.unit
class TestTemplatorRendering:
    """Tests for render() method."""

    def test_render_simple_template(self, sample_template):
        """Test: Rendering a simple template."""
        templator = Templator(folder=str(sample_template))

        result = templator.render(
            "test.html",
            content={"title": "Test", "heading": "Hello", "content": "World"},
        )

        # Check that result contains expected elements
        assert "Test" in result
        assert "Hello" in result
        assert "World" in result
        assert "<html>" in result

    def test_render_with_kwargs(self, sample_template):
        """Test: Rendering with kwargs parameters."""
        templator = Templator(folder=str(sample_template))

        result = templator.render(
            "test.html",
            content={"title": "MyTitle", "heading": "MyHeading", "content": "MyContent"},
        )

        assert "MyTitle" in result
        assert "MyHeading" in result
        assert "MyContent" in result

    def test_render_with_content_and_kwargs(self, sample_template):
        """Test: Rendering with content and kwargs (kwargs have priority)."""
        templator = Templator(folder=str(sample_template))

        result = templator.render(
            "test.html",
            content={"title": "FromContent", "heading": "Test"},
            extra_field="FromKwargs",  # Additional field via kwargs
        )

        # Both content and kwargs should be present
        assert "FromContent" in result
        assert "Test" in result

    def test_render_empty_context(self, temp_template_dir):
        """Test: Rendering without context."""
        # Create simple template without variables
        template_file = temp_template_dir / "simple.html"
        template_file.write_text("<h1>Static Content</h1>")

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("simple.html")

        assert "Static Content" in result

    def test_render_none_content(self, sample_template):
        """Test: content=None should work."""
        templator = Templator(folder=str(sample_template))

        # Should not error with content=None
        result = templator.render(
            "test.html", content=None, title="Test", heading="H1"
        )

        assert "Test" in result


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
class TestTemplatorErrors:
    """Error handling tests."""

    def test_render_nonexistent_template(self, temp_template_dir):
        """Test: Error when rendering nonexistent template."""
        templator = Templator(folder=str(temp_template_dir))

        with pytest.raises(TemplateNotFound):
            templator.render("nonexistent.html")

    def test_render_invalid_content_type(self, sample_template):
        """Test: TypeError for invalid content type."""
        templator = Templator(folder=str(sample_template))

        # content must be dict, not str
        with pytest.raises(TypeError, match="Content must be a dictionary"):
            templator.render("test.html", content="invalid string")

    def test_render_content_not_dict_list(self, sample_template):
        """Test: TypeError when passing list to content."""
        templator = Templator(folder=str(sample_template))

        with pytest.raises(TypeError, match="Content must be a dictionary"):
            templator.render("test.html", content=["item1", "item2"])

    def test_render_content_not_dict_number(self, sample_template):
        """Test: TypeError when passing number to content."""
        templator = Templator(folder=str(sample_template))

        with pytest.raises(TypeError, match="Content must be a dictionary"):
            templator.render("test.html", content=123)


# ============================================================================
# Tests with Various Template Types
# ============================================================================


@pytest.mark.unit
class TestTemplatorVariousTemplates:
    """Tests with various template types."""

    def test_render_template_with_loop(self, temp_template_dir):
        """Test: Template with loop."""
        template_content = """
        <ul>
        {% for item in items %}
            <li>{{ item }}</li>
        {% endfor %}
        </ul>
        """
        template_file = temp_template_dir / "loop.html"
        template_file.write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("loop.html", items=["Apple", "Banana", "Cherry"])

        assert "<li>Apple</li>" in result
        assert "<li>Banana</li>" in result
        assert "<li>Cherry</li>" in result

    def test_render_template_with_conditional(self, temp_template_dir):
        """Test: Template with conditionals."""
        template_content = """
        {% if show_message %}
            <p>{{ message }}</p>
        {% endif %}
        """
        template_file = temp_template_dir / "conditional.html"
        template_file.write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))

        # With condition True
        result_true = templator.render(
            "conditional.html", show_message=True, message="Hello"
        )
        assert "Hello" in result_true

        # With condition False
        result_false = templator.render(
            "conditional.html", show_message=False, message="Hello"
        )
        assert "Hello" not in result_false

    def test_render_template_with_filters(self, temp_template_dir):
        """Test: Template with Jinja2 filters."""
        template_content = """
        <p>{{ text|upper }}</p>
        <p>{{ text|lower }}</p>
        """
        template_file = temp_template_dir / "filters.html"
        template_file.write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("filters.html", text="Hello World")

        assert "HELLO WORLD" in result
        assert "hello world" in result


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestTemplatorIntegration:
    """Templator integration tests."""

    def test_multiple_templates_in_same_folder(self, temp_template_dir):
        """Test: Multiple templates in one folder."""
        # Create multiple templates
        (temp_template_dir / "page1.html").write_text("<h1>Page 1</h1>")
        (temp_template_dir / "page2.html").write_text("<h1>Page 2</h1>")
        (temp_template_dir / "page3.html").write_text("<h1>Page 3</h1>")

        templator = Templator(folder=str(temp_template_dir))

        # Render all three
        result1 = templator.render("page1.html")
        result2 = templator.render("page2.html")
        result3 = templator.render("page3.html")

        assert "Page 1" in result1
        assert "Page 2" in result2
        assert "Page 3" in result3

    def test_template_inheritance(self, temp_template_dir):
        """Test: Template inheritance (Jinja2 extends)."""
        # Base template
        base_template = """
        <!DOCTYPE html>
        <html>
        <head><title>{% block title %}Default{% endblock %}</title></head>
        <body>{% block content %}{% endblock %}</body>
        </html>
        """
        (temp_template_dir / "base.html").write_text(base_template)

        # Child template
        child_template = """
        {% extends "base.html" %}
        {% block title %}Child Page{% endblock %}
        {% block content %}<h1>Child Content</h1>{% endblock %}
        """
        (temp_template_dir / "child.html").write_text(child_template)

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("child.html")

        assert "Child Page" in result
        assert "Child Content" in result
        assert "<html>" in result

    def test_complex_context_data(self, temp_template_dir):
        """Test: Complex data structures in context."""
        template_content = """
        <h1>{{ user.name }}</h1>
        <p>Email: {{ user.email }}</p>
        <ul>
        {% for post in user.posts %}
            <li>{{ post.title }} - {{ post.likes }} likes</li>
        {% endfor %}
        </ul>
        """
        (temp_template_dir / "complex.html").write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))

        context = {
            "user": {
                "name": "Alice",
                "email": "alice@example.com",
                "posts": [
                    {"title": "First Post", "likes": 10},
                    {"title": "Second Post", "likes": 25},
                ],
            }
        }

        result = templator.render("complex.html", content=context)

        assert "Alice" in result
        assert "alice@example.com" in result
        assert "First Post" in result
        assert "10 likes" in result
        assert "Second Post" in result
        assert "25 likes" in result


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestTemplatorEdgeCases:
    """Edge case tests."""

    def test_template_with_special_characters(self, temp_template_dir):
        """Test: Template with special characters."""
        template_content = """
        <p>{{ text }}</p>
        """
        (temp_template_dir / "special.html").write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("special.html", text="<script>alert('XSS')</script>")

        # Jinja2 should escape HTML by default
        assert "&lt;script&gt;" in result or "alert" not in result

    def test_empty_template(self, temp_template_dir):
        """Test: Empty template."""
        (temp_template_dir / "empty.html").write_text("")

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("empty.html")

        assert result == ""

    def test_template_with_unicode(self, temp_template_dir):
        """Test: Template with Unicode characters."""
        template_content = "<p>{{ message }}</p>"
        (temp_template_dir / "unicode.html").write_text(template_content)

        templator = Templator(folder=str(temp_template_dir))
        result = templator.render("unicode.html", message="Привет, мир! 🌍")

        assert "Привет, мир!" in result
        assert "🌍" in result
