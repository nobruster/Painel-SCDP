import re
from pathlib import Path

CI = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"
USES = re.compile(r"^\s*-?\s*uses:\s*(\S+)", re.M)
SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def _usos():
    return [u for u in USES.findall(CI.read_text(encoding="utf-8")) if not u.startswith("./")]


def test_ha_actions():
    assert _usos()


def test_todo_uses_fixado_por_sha_de_40_hex():
    ruins = [u for u in _usos() if not SHA.match(u)]
    assert not ruins, ruins


def test_sha_tem_versao_em_comentario():
    for linha in CI.read_text(encoding="utf-8").splitlines():
        if "uses:" in linha and "@" in linha and "./" not in linha:
            assert re.search(r"#\s*v\d", linha), linha
