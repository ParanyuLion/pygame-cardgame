from unittest.mock import MagicMock
from src.use_cases.start_run import StartRunUseCase


def _make_use_case():
    run_repo = MagicMock()
    card_repo = MagicMock()
    card_repo.get_starting_deck.return_value = []
    return StartRunUseCase(run_repo, card_repo), run_repo


def test_start_run_creates_three_floors():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    assert len(run.floors) == 3


def test_start_run_each_floor_has_four_nodes():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    assert all(len(f) == 4 for f in run.floors)


def test_start_run_first_node_is_combat():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    assert run.current_node().node_type == "combat"


def test_start_run_last_node_per_floor_is_boss():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    for floor_nodes in run.floors:
        assert floor_nodes[-1].node_type == "boss"


def test_start_run_floor3_boss_has_two_enemies():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    boss = run.floors[2][-1]
    assert len(boss.enemies) == 2


def test_start_run_saves_to_repo():
    use_case, run_repo = _make_use_case()
    run = use_case.execute()
    run_repo.save.assert_called_once_with(run)


def test_start_run_player_hp_is_30():
    use_case, _ = _make_use_case()
    run = use_case.execute()
    assert run.player_hp == 30
    assert run.player_max_hp == 30
