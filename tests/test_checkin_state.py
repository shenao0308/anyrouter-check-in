import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from checkin import (
	format_check_in_notification,
	generate_balance_hash,
	load_balance_history,
	save_balance_history,
)


def test_balance_hash_changes_when_quota_changes():
	before = {'account_1': {'quota': 100.0, 'used': 20.0}}
	after = {'account_1': {'quota': 125.0, 'used': 20.0}}

	assert generate_balance_hash(before) != generate_balance_hash(after)


def test_balance_hash_changes_when_used_quota_changes():
	before = {'account_1': {'quota': 100.0, 'used': 20.0}}
	after = {'account_1': {'quota': 100.0, 'used': 21.0}}

	assert generate_balance_hash(before) != generate_balance_hash(after)


def test_balance_hash_is_stable_for_equivalent_balances():
	left = {
		'account_2': {'quota': 50.0, 'used': 1.0},
		'account_1': {'quota': 100.0, 'used': 20.0},
	}
	right = {
		'account_1': {'used': 20.0, 'quota': 100.0},
		'account_2': {'used': 1.0, 'quota': 50.0},
	}

	assert generate_balance_hash(left) == generate_balance_hash(right)


def test_balance_history_roundtrip(monkeypatch, tmp_path):
	history_file = tmp_path / 'balance_history.json'
	monkeypatch.setattr('checkin.BALANCE_HISTORY_FILE', str(history_file))

	assert load_balance_history() == {}

	data = {
		'我的AnyRouter': {'quota': 477.52, 'used': 195.90, 'updated_at': '2026-11-06 08:00:00'},
		'我的AgentRouter': {'quota': 1248.82, 'used': 101.18, 'updated_at': '2026-11-06 08:00:00'},
	}
	save_balance_history(data)

	loaded = load_balance_history()
	assert loaded == data


def test_format_notification_agentrouter_no_change():
	detail = {
		'name': '我的AgentRouter',
		'needs_manual_check_in': False,
		'before_quota': 1248.82,
		'before_used': 101.18,
		'after_quota': 1248.82,
		'after_used': 101.18,
		'check_in_reward': 0.0,
		'usage_increase': 0.0,
		'balance_change': 0.0,
		'is_history_diff': False,
		'success': True,
	}
	result = format_check_in_notification(detail)
	assert '当前余额: $1248.82' in result
	assert '累计消耗: $101.18' in result
	assert '今日打卡已自动激活生效' in result
	assert '签到前' not in result
	assert '签到后' not in result


def test_format_notification_anyrouter_no_change():
	detail = {
		'name': '我的AnyRouter',
		'needs_manual_check_in': True,
		'before_quota': 477.52,
		'before_used': 195.90,
		'after_quota': 477.52,
		'after_used': 195.90,
		'check_in_reward': 0.0,
		'usage_increase': 0.0,
		'balance_change': 0.0,
		'is_history_diff': False,
		'success': True,
	}
	result = format_check_in_notification(detail)
	assert '当前余额: $477.52' in result
	assert '累计消耗: $195.90' in result
	assert '今日已签到，额度无变化' in result
	assert '签到前' not in result
	assert '签到后' not in result


def test_format_notification_with_reward():
	detail = {
		'name': '我的AnyRouter',
		'needs_manual_check_in': True,
		'before_quota': 452.52,
		'before_used': 195.90,
		'after_quota': 477.52,
		'after_used': 195.90,
		'check_in_reward': 25.0,
		'usage_increase': 0.0,
		'balance_change': 25.0,
		'is_history_diff': False,
		'success': True,
	}
	result = format_check_in_notification(detail)
	assert '签到前' in result
	assert '余额: $452.52' in result
	assert '签到后' in result
	assert '余额: $477.52' in result
	assert '签到获得: +$25.00' in result


def test_format_notification_with_usage_only():
	detail = {
		'name': '我的AnyRouter',
		'needs_manual_check_in': True,
		'before_quota': 477.52,
		'before_used': 195.90,
		'after_quota': 476.52,
		'after_used': 196.90,
		'check_in_reward': 0.0,
		'usage_increase': 1.0,
		'balance_change': -1.0,
		'is_history_diff': True,
		'success': True,
	}
	result = format_check_in_notification(detail)
	assert '当前余额: $476.52' in result
	assert '期间消耗: $1.00' in result
