"""No-GPU tests for decisions_api / decisions_server: schema of the OpenRouter Decisions API, error codes, auth, windowing.
    cd code && python -m pytest test_decisions_api.py -q
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # code/: eval, modeling_openjev, openjev_decide
import numpy as np
import pytest
from fastapi.testclient import TestClient

import decisions_api as da
import decisions_server as ds

TUTORIAL = {
    "model": "typesafe/jev-1.13",
    "state": {"customer_tier": "enterprise",
              "ticket": "My checkout page shows a blank screen after I click Pay. I have tried two browsers."},
    "questions": {
        "is_bug": {"type": "noul", "instructions": "Is the customer reporting a software defect?",
                   "criteria": {"true": "The customer describes broken or unexpected product behavior.",
                                "false": "The customer is asking a question or requesting a feature."}},
        "team": {"type": "choice", "instructions": "Which team should own this ticket?",
                 "criteria": {"payments": "Checkout, billing, or payment processing issues.",
                              "frontend": "Rendering, layout, or browser compatibility issues.",
                              "account": "Login, permissions, or profile issues."}},
        "urgency": {"type": "score", "instructions": "How urgent is this ticket?",
                    "criteria": ["Can wait for the next release", "Should be fixed this week",
                                 "Blocking revenue right now"]},
    },
}


def fake_scores(pairs):
    """Stand-in model: hypotheses naming payments / 'yes' / the last score level are entailed."""
    return np.array([0.9 if any(k in h for k in (" is payments:", " is yes:", " is 2:")) else 0.1 for _, h in pairs])


@pytest.fixture
def api(monkeypatch):
    async def fake_classify(pairs, image=None):
        return fake_scores(pairs), 100 * len(pairs)
    monkeypatch.setattr(ds, "classify", fake_classify)
    monkeypatch.setattr(ds, "API_KEY", "")
    return TestClient(ds.app)


def test_shared_strings_match_openjev_decide():
    torch = pytest.importorskip("torch")  # openjev_decide imports torch + transformers
    import openjev_decide as od
    assert od.TEMPLATE == da.HYPOTHESIS and od.WINDOW_CHARS == da.WINDOW_CHARS


def test_pairs_use_the_training_format():
    plan = da.build_plan(TUTORIAL)
    hyps = [h for _, h in plan.pairs]
    assert hyps[0] == ('The answer to "Is the customer reporting a software defect?" is no: '
                       'The customer is asking a question or requesting a feature.')
    assert hyps[1].startswith('The answer to "Is the customer reporting a software defect?" is yes: ')
    assert any(h.startswith('The answer to "How urgent is this ticket?" is 2: Blocking') for h in hyps)
    assert len(plan.pairs) == 2 + 3 + 3
    assert plan.pairs[0][0].startswith('{"customer_tier": "enterprise"')  # object state -> json


@pytest.mark.parametrize("path", ["/api/alpha/decisions", "/api/v1/systemone", "/v1/systemone"])
def test_tutorial_response_shape(api, path):
    r = api.post(path, json=TUTORIAL)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["id"].startswith("gen-dec-") and j["model"] and j["provider"]
    assert set(j["usage"]) == {"input_tokens", "output_tokens", "cost"} and j["usage"]["output_tokens"] == 0
    a = j["answers"]
    assert a["is_bug"]["type"] == "noul" and a["is_bug"]["noul"] == pytest.approx(0.9, abs=1e-3)
    t = a["team"]
    assert t["type"] == "choice" and t["choice"] == "payments" and set(t["probabilities"]) == {"payments", "frontend", "account"}
    assert sum(t["probabilities"].values()) == pytest.approx(1, abs=1e-3) and 0 <= t["confidence"] <= 1
    u = a["urgency"]
    assert u["type"] == "score" and set(u["probabilities"]) == {"0", "1", "2"}
    assert u["legend"] == {"0": "Can wait for the next release", "1": "Should be fixed this week",
                           "2": "Blocking revenue right now"}
    assert u["score"] == pytest.approx(0.1 / 1.1 * 1 + 0.9 / 1.1 * 2, abs=1e-3)


def test_confidence_bounds():
    assert da.confidence([1.0, 0.0, 0.0]) == pytest.approx(1.0)
    assert da.confidence([1 / 3] * 3) == pytest.approx(0.0, abs=1e-9)
    assert da.confidence([1.0]) == 1.0


@pytest.mark.parametrize("mut,code", [
    (lambda r: r.pop("model"), 400),
    (lambda r: r.pop("state"), 400),
    (lambda r: r.update(state=5), 400),
    (lambda r: r.update(questions={}), 400),
    (lambda r: r["questions"]["team"].update(type="rank"), 400),
    (lambda r: r["questions"]["is_bug"].update(criteria={"true": "x"}), 400),
    (lambda r: r["questions"]["team"].update(criteria=["a"]), 400),
    (lambda r: r["questions"]["urgency"].update(criteria={"a": "b"}), 400),
    (lambda r: r["questions"]["urgency"].update(criteria=[]), 400),
    (lambda r: r.update(state="x" * (da.MAX_STATE_CHARS + 1)), 413),
])
def test_bad_requests(api, mut, code):
    import copy
    req = copy.deepcopy(TUTORIAL)
    mut(req)
    r = api.post("/api/alpha/decisions", json=req)
    assert r.status_code == code
    assert r.json()["error"]["code"] == code and r.json()["error"]["message"]


def test_invalid_json_and_auth(api, monkeypatch):
    assert api.post("/api/alpha/decisions", content=b"{nope").status_code == 400
    monkeypatch.setattr(ds, "API_KEY", "secret")
    assert api.post("/api/alpha/decisions", json=TUTORIAL).status_code == 401
    assert api.post("/api/alpha/decisions", json=TUTORIAL, headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert api.post("/api/alpha/decisions", json=TUTORIAL, headers={"Authorization": "Bearer secret"}).status_code == 200


def test_long_state_is_windowed_not_cut():
    req = {"model": "m", "state": "a" * 60_000, "questions": {"q": {"type": "noul", "instructions": "i",
           "criteria": {"true": "t", "false": "f"}}}}
    plan = da.build_plan(req)
    assert plan.questions[0].n_windows == 3 and len(plan.pairs) == 6
    assert plan.pairs[-1][0][-1] == "a" and max(len(p) for p, _ in plan.pairs) == da.WINDOW_CHARS
    # only window 0 supports "yes": max over windows per option, then normalise -> yes = 0.9 / (0.9 + 0.1)
    ent = np.array([0.1, 0.9, 0.1, 0.1, 0.1, 0.1])  # per window: [no, yes]
    assert da.assemble(plan, ent)["q"]["noul"] == pytest.approx(0.9, abs=1e-3)
    ent = np.array([0.1, 0.2, 0.9, 0.1, 0.1, 0.1])  # window 1 supports "no" strongly
    assert da.assemble(plan, ent)["q"]["noul"] == pytest.approx(0.2 / 1.1, abs=1e-3)


def test_softmax_ent_order():
    p = da.softmax_ent([[0, 10, 0], [10, 0, 0]])  # label 1 = entailment
    assert p[0] > 0.99 and p[1] < 0.01


def test_health_loading(monkeypatch):
    async def boom(*a, **k):
        raise __import__("httpx").ConnectError("down")
    monkeypatch.setattr(ds.client(), "get", boom)
    assert TestClient(ds.app).get("/health").status_code == 503


def test_noul_omitted_criteria_uses_existing_bare_yes_no_rubric(api):
    req = {"model": "m", "state": "A duplicate invoice was submitted.",
           "questions": {"duplicate": {"type": "noul", "instructions": "This invoice is a duplicate."}}}
    plan = da.build_plan(req)
    assert [h for _, h in plan.pairs] == [
        'The answer to "This invoice is a duplicate." is no: no',
        'The answer to "This invoice is a duplicate." is yes: yes',
    ]
    response = api.post("/v1/systemone", json=req)
    assert response.status_code == 200
    assert response.json()["answers"]["duplicate"]["type"] == "noul"
