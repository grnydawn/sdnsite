import pytest

from apps.content.templatetags.content_tags import render_markdown


class TestRenderMarkdownHeadings:
    """Test heading conversion."""

    def test_h1_heading(self):
        result = render_markdown("# Hello")
        assert "<h1>Hello</h1>" in result

    def test_h2_heading(self):
        result = render_markdown("## Subheading")
        assert "<h2>Subheading</h2>" in result


class TestRenderMarkdownInlineFormatting:
    """Test inline formatting."""

    def test_bold(self):
        result = render_markdown("**bold**")
        assert "<strong>bold</strong>" in result

    def test_italic(self):
        result = render_markdown("*italic*")
        assert "<em>italic</em>" in result


class TestRenderMarkdownCodeBlocks:
    """Test fenced code blocks with Pygments syntax highlighting."""

    def test_fenced_code_block_has_codehilite_class(self):
        md = '```python\nprint("hi")\n```'
        result = render_markdown(md)
        assert "codehilite" in result

    def test_fenced_code_preserves_class_on_span(self):
        """Pygments emits <span class="..."> for tokens; nh3 must preserve class."""
        md = '```python\nprint("hi")\n```'
        result = render_markdown(md)
        # Pygments wraps tokens in spans with class attributes
        assert 'class="' in result


class TestRenderMarkdownSanitization:
    """Test nh3 sanitization strips dangerous tags."""

    def test_script_tag_stripped(self):
        result = render_markdown("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "alert(1)" not in result

    def test_iframe_stripped(self):
        result = render_markdown('<iframe src="http://evil.com"></iframe>')
        assert "<iframe" not in result

    def test_form_stripped(self):
        result = render_markdown('<form action="/hack"><input></form>')
        assert "<form" not in result

    def test_event_handler_stripped(self):
        result = render_markdown('<div onmouseover="alert(1)">hover</div>')
        assert "onmouseover" not in result


class TestRenderMarkdownEdgeCases:
    """Test empty and None inputs."""

    def test_empty_string(self):
        result = render_markdown("")
        assert result == ""

    def test_none_input(self):
        result = render_markdown(None)
        assert result == ""


class TestRenderMarkdownTables:
    """Test markdown table rendering."""

    def test_table_renders(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = render_markdown(md)
        assert "<table>" in result or "<table" in result
        assert "<td>" in result


class TestRenderMarkdownClassPreservation:
    """Test that class attributes are preserved on elements."""

    def test_codehilite_div_class_preserved(self):
        md = '```python\nx = 1\n```'
        result = render_markdown(md)
        assert 'class="codehilite"' in result
