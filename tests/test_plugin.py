"""Tests for the SEO Pipeline plugin structure."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_root_init_py():
    """Root __init__.py must expose register() for Hermes plugin loading."""
    init = ROOT / "__init__.py"
    assert init.exists(), f"Missing root {init}"
    content = init.read_text()
    assert "__version__" in content
    assert "def register(ctx)" in content, "Missing register() entry point"


def test_plugin_yaml():
    """plugin.yaml must exist and be valid Hermes plugin manifest."""
    yaml_path = ROOT / "plugin.yaml"
    assert yaml_path.exists(), "Missing plugin.yaml"
    content = yaml_path.read_text()
    assert "name: seo-pipeline" in content
    assert "skills:" in content or "type: skills" in content


def test_agents_md():
    """AGENTS.md must exist (canonical pipeline instructions)."""
    agents = ROOT / "AGENTS.md"
    assert agents.exists(), "Missing AGENTS.md"
    content = agents.read_text()
    assert "Stage 1" in content
    assert "BROWSER_USE_API_KEY" in content


def test_skills():
    """Each registered skill must have a SKILL.md."""
    skills_dir = ROOT / "skills"
    assert skills_dir.is_dir(), "Missing skills/ directory"
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
    assert len(skill_dirs) >= 2, "Expected at least 2 skills"
    for sd in skill_dirs:
        assert (sd / "SKILL.md").exists(), f"Missing SKILL.md in {sd.name}"


def test_devin_plugin():
    """Devin plugin manifest must be valid JSON."""
    path = ROOT / ".devin-plugin" / "plugin.json"
    assert path.exists()
    data = __import__("json").loads(path.read_text())
    assert data["name"] == "seo-pipeline"


def test_claude_plugin():
    """Claude Code plugin manifest must exist."""
    path = ROOT / ".claude-plugin" / "plugin.json"
    assert path.exists()
    data = __import__("json").loads(path.read_text())
    assert data["name"] == "seo-pipeline"


def test_claude_marketplace():
    """Claude Code marketplace.json must exist."""
    path = ROOT / ".claude-plugin" / "marketplace.json"
    assert path.exists()
    data = __import__("json").loads(path.read_text())
    assert len(data["plugins"]) >= 1
    assert data["plugins"][0]["name"] == "seo-pipeline"


def test_codex_plugin():
    """Codex plugin manifest must exist."""
    path = ROOT / ".codex-plugin" / "plugin.json"
    assert path.exists()
    data = __import__("json").loads(path.read_text())
    assert data["name"] == "seo-pipeline"


def test_opencode_config():
    """OpenCode configuration must exist."""
    json_path = ROOT / "opencode.json"
    assert json_path.exists()
    data = __import__("json").loads(json_path.read_text())
    assert "agent" in data

    md_path = ROOT / ".opencode" / "command" / "seo-pipeline.md"
    assert md_path.exists(), "Missing .opencode/command/seo-pipeline.md"

    plugin_path = ROOT / ".opencode" / "plugins" / "seo-pipeline.mjs"
    assert plugin_path.exists(), "Missing .opencode/plugins/seo-pipeline.mjs"


def test_pi_extension():
    """Pi agent harness extension must exist."""
    pkg = ROOT / "pi-extension" / "package.json"
    assert pkg.exists()
    js = ROOT / "pi-extension" / "index.js"
    assert js.exists()
    content = js.read_text()
    assert "AGENTS.md" in content or "PIPELINE_INSTRUCTIONS" in content


def test_gemini_extension():
    """Gemini extension manifest must exist."""
    path = ROOT / "gemini-extension.json"
    assert path.exists()
    data = __import__("json").loads(path.read_text())
    assert data["name"] == "seo-pipeline"


def test_hooks():
    """Lifecycle hook files must have valid structure with real commands."""
    claude_hooks = ROOT / "hooks" / "claude-codex-hooks.json"
    assert claude_hooks.exists()
    data = _load_json(claude_hooks)
    assert "hooks" in data
    assert "SessionStart" in data["hooks"]
    hook_list = data["hooks"]["SessionStart"][0]["hooks"]
    assert len(hook_list) >= 1
    cmd = hook_list[0]["command"]
    assert "BROWSER_USE_API_KEY" in cmd, "Hook must check API key"
    assert "MISSING" in cmd, "Hook must report missing key"

    copilot_hooks = ROOT / "hooks" / "copilot-hooks.json"
    assert copilot_hooks.exists()
    data = _load_json(copilot_hooks)
    assert "hooks" in data
    assert "sessionStart" in data["hooks"]
    cmd = data["hooks"]["sessionStart"][0]["bash"]
    assert "BROWSER_USE_API_KEY" in cmd, "Copilot hook must check API key"
    assert "MISSING" in cmd, "Copilot hook must report missing key"


def test_plugin_yaml_hooks_match_init():
    """provides_hooks in plugin.yaml must have implementations in __init__.py."""
    yaml_content = (ROOT / "plugin.yaml").read_text()
    init_content = (ROOT / "__init__.py").read_text()
    if "provides_hooks:" in yaml_content:
        # extract hook names declared in plugin.yaml
        import re

        hook_names = re.findall(
            r"^\s+-\s+(.+)$",
            yaml_content.split("provides_hooks:")[1].split("\n\n")[0],
            re.M,
        )
        for h in hook_names:
            assert h.strip() in init_content, (
                f"Hook '{h.strip()}' declared in plugin.yaml but not implemented in __init__.py"
            )


def test_commands():
    """Hermes command definitions must exist."""
    cmd_dir = ROOT / "commands"
    assert cmd_dir.is_dir()
    cmd_files = list(cmd_dir.glob("*.toml"))
    assert len(cmd_files) >= 1


def test_examples():
    """Usage examples must exist."""
    examples = ROOT / "examples" / "README.md"
    assert examples.exists()


def test_after_install():
    """After-install instructions must exist."""
    path = ROOT / "after-install.md"
    assert path.exists()


def test_env_example():
    """Environment template must exist."""
    path = ROOT / ".env.example"
    assert path.exists()


def test_pyproject():
    """pyproject.toml must exist with correct package name."""
    path = ROOT / "pyproject.toml"
    assert path.exists()
    content = path.read_text()
    assert 'name = "seo-pipeline"' in content


def test_copilot_instructions():
    """GitHub Copilot instructions must exist."""
    path = ROOT / ".github" / "copilot-instructions.md"
    assert path.exists()


def test_clinerules():
    """Cline rules must exist."""
    path = ROOT / ".clinerules" / "seo-pipeline.md"
    assert path.exists()


def test_cursor_rules():
    """Cursor rules must exist."""
    path = ROOT / ".cursor" / "rules" / "seo-pipeline.mdc"
    assert path.exists()


def test_windsurf_rules():
    """Windsurf rules must exist."""
    path = ROOT / ".windsurf" / "rules" / "seo-pipeline.md"
    assert path.exists()
