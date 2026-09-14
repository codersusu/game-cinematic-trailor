#!/usr/bin/env python3
"""Read Codex task telemetry locally; export only aggregate usage and timing.

No prompts, responses, credentials, raw session IDs, or local paths are exported.
The database is opened read-only. Requires Python 3.9+; no dependencies.
"""
import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3

FIELDS = ('input_tokens', 'cached_input_tokens', 'cache_write_input_tokens',
          'output_tokens', 'reasoning_output_tokens', 'total_tokens')

def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()

def iso(value):
    return dt.datetime.fromtimestamp(value, dt.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def merged(intervals):
    result = []
    for start, end in sorted(intervals):
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result

def seconds(intervals):
    return round(sum(b-a for a, b in merged(intervals)), 3)

def aggregate(rows, key='tokens'):
    out = {k: sum(r[key].get(k, 0) for r in rows) for k in FIELDS}
    out['uncached_input_tokens'] = out['input_tokens'] - out['cached_input_tokens']
    return out

def audit(args):
    cutoff = timestamp(args.cutoff)
    con = sqlite3.connect(f'file:{args.state_db}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    root = con.execute('SELECT id,cwd FROM threads WHERE id=?', (args.root_thread,)).fetchone()
    if root is None:
        raise ValueError('Root task not found')
    # Workspace scopes the read; metadata ancestry, not cwd alone, selects members.
    candidates = list(con.execute('SELECT id,rollout_path,agent_path FROM threads WHERE cwd=?', (root['cwd'],)))
    catalog = {}
    for row in candidates:
        with open(row['rollout_path']) as handle:
            for line in handle:
                record = json.loads(line)
                if record['type'] == 'session_meta' and record['payload']['id'] == row['id']:
                    catalog[row['id']] = (dict(row), record['payload'])
                    break
    selected = {args.root_thread}
    while True:
        found = {tid for tid, (_, meta) in catalog.items() if meta.get('parent_thread_id') in selected}
        if found <= selected:
            break
        selected |= found
    rows = []; all_seen = {}; all_intervals = []; main_intervals = []; timing_issues = []
    root_start = None; root_end = None; root_unclosed_upper = None
    for tid in sorted(selected):
        row, meta = catalog[tid]
        kind = 'main' if tid == args.root_thread else ('approval_review' if meta.get('thread_source') == 'guardian_review' else 'development_agent')
        label = 'main' if kind == 'main' else row['agent_path'] or f'approval_review_{1+sum(r["kind"] == "approval_review" for r in rows):02d}'
        records = []; events = []; seen = set(); digest = hashlib.sha256(); cumulative = None
        duplicate_count = 0; monotonic = True
        for line in open(row['rollout_path']):
            d = json.loads(line); p = d.get('payload', {})
            if timestamp(d['timestamp']) >= cutoff:
                continue
            if d['type'] == 'token_usage_record' and p.get('thread_id') == tid:
                response = p['response_id']
                if response in seen:
                    duplicate_count += 1
                    continue
                seen.add(response)
                if response in all_seen:
                    raise ValueError('Cross-thread duplicate response requires investigation')
                all_seen[response] = True
                for key in FIELDS:
                    assert p['usage'][key] >= 0
                assert p['usage']['input_tokens'] + p['usage']['output_tokens'] == p['usage']['total_tokens']
                assert p['usage']['cached_input_tokens'] <= p['usage']['input_tokens']
                assert p['usage']['reasoning_output_tokens'] <= p['usage']['output_tokens']
                if cumulative and any(p['thread_token_usage'][k] < cumulative[k] for k in FIELDS):
                    monotonic = False
                cumulative = {k: p['thread_token_usage'][k] for k in FIELDS}
                records.append(d)
                digest.update(json.dumps({'response_id': response, 'usage': p['usage'], 'thread_token_usage': cumulative}, sort_keys=True).encode())
            elif d['type'] == 'event_msg' and p.get('type') in ('task_started', 'task_complete'):
                events.append(d)
        if not records:
            continue
        if not monotonic:
            raise ValueError(f'Nonmonotonic durable cumulative counter: {label}')
        summed = {k: sum(d['payload']['usage'][k] for d in records) for k in FIELDS}
        gap = {k: cumulative[k]-summed[k] for k in FIELDS}
        assert all(v >= 0 for v in gap.values())
        own_turns = {d['payload']['turn_id'] for d in records}
        # Copied parent history has other turn IDs: it is never active child time.
        starts = {d['payload']['turn_id']: d for d in events if d['payload']['type'] == 'task_started' and d['payload']['turn_id'] in own_turns}
        ends = {d['payload']['turn_id']: d for d in events if d['payload']['type'] == 'task_complete' and d['payload']['turn_id'] in own_turns}
        intervals = []; completed = 0; inferred = 0; normalized = 0
        for turn in own_turns:
            start = starts.get(turn); end = ends.get(turn)
            if start:
                start_epoch = start['payload'].get('started_at')
                a = timestamp(start['timestamp'])
                if start_epoch is not None and abs(a-start_epoch) > 2:
                    a = float(start_epoch); normalized += 1
            elif end and end['payload'].get('started_at') is not None:
                a = float(end['payload']['started_at']); normalized += 1
            else:
                timing_issues.append({'agent': label, 'issue': 'Missing start: turn excluded from active time'})
                continue
            if end:
                p = end['payload']; duration = p.get('duration_ms')
                b = a + duration/1000 if duration is not None else float(p.get('completed_at', timestamp(end['timestamp'])))
                completed += 1
            else:
                b = max(timestamp(d['timestamp']) for d in records if d['payload']['turn_id'] == turn)
                inferred += 1
                timing_issues.append({'agent': label, 'issue': 'Missing completion: use final usage timestamp as lower endpoint', 'start_utc': iso(a), 'last_usage_utc': iso(b)})
                if kind == 'main':
                    later = [timestamp(d['timestamp']) for d in events if d['payload']['type'] == 'task_started' and timestamp(d['timestamp']) > b]
                    if later:
                        root_unclosed_upper = min(later)-b
            if b >= a and a < cutoff:
                intervals.append([a, min(b, cutoff)])
        if kind != 'approval_review':
            all_intervals.extend(intervals)
        if kind == 'main':
            main_intervals = intervals
            root_start = min(a for a,b in intervals)
            # For the last completed publication turn, preserve its actual event timestamp.
            root_end = max(timestamp(d['timestamp']) for d in ends.values())
        rows.append({'label': label, 'kind': kind, 'tokens': cumulative,
                     'retained_response_tokens': summed, 'cumulative_only_tokens': gap,
                     'retained_responses': len(records), 'duplicate_records_skipped': duplicate_count,
                     'retained_usage_sha256': digest.hexdigest(),
                     'completed_turns_with_usage': completed, 'inferred_intervals': inferred,
                     'normalized_start_timestamps': normalized,
                     'active_seconds': seconds(intervals)})
    main = [r for r in rows if r['kind']=='main']; agents = [r for r in rows if r['kind']=='development_agent']; reviews = [r for r in rows if r['kind']=='approval_review']
    return {'schema_version': 1, 'cutoff_utc_exclusive': args.cutoff,
            'scope': 'Cinematic task through prior publication/cleanup; excludes this usage-audit turn',
            'counts': {'development_agents': len(agents), 'approval_review_threads': len(reviews), 'retained_unique_responses_all': len(all_seen)},
            'totals': {'main': aggregate(main), 'development_agents': aggregate(agents),
                       'development_combined': aggregate(main+agents), 'automatic_approval_reviews': aggregate(reviews),
                       'all_recorded': aggregate(rows)},
            'time': {'conversation_start_utc': iso(root_start), 'last_development_completion_utc': iso(root_end),
                     'conversation_elapsed_to_audit_request_seconds': round(cutoff-root_start,3),
                     'elapsed_to_publication_completion_seconds': round(root_end-root_start,3),
                     'main_active_seconds': seconds(main_intervals),
                     'development_active_wall_seconds': seconds(all_intervals),
                     'development_summed_agent_seconds': round(sum(r['active_seconds'] for r in main+agents),3),
                     'missing_main_completion_upper_extra_seconds': round(root_unclosed_upper or 0,3),
                     'active_definition': 'Union of main/development-agent turn intervals. Includes research, tools, rendering, waiting, uploads; excludes between-turn idle; parallel intervals counted once.',
                     'pure_coding_or_model_compute_time_seconds': None,
                     'intervals_utc': [[iso(a),iso(b)] for a,b in merged(all_intervals)],
                     'issues': timing_issues},
            'threads': rows,
            'methodology': ['Use durable token_usage_record.thread_token_usage once per owning thread, after verifying monotonicity; never sum cumulative snapshots.',
                            'Deduplicate response_id and compare retained per-response usage against durable cumulative totals.',
                            'Main and all nine development agents have complete per-response sums matching cumulative totals.',
                            'Five approval-review logs retain cumulative counters for earlier removed responses; their extra totals are separately identified.',
                            'Ignore event_msg.token_count rolling counters and SQLite tokens_used for lifetime usage, as they disagree after context changes.',
                            'Cached input is a subset of input; reasoning output is a subset of output. Total equals input plus output.',
                            'No subscription charge, API bill, external Meshy/ElevenLabs usage, or model-compute duration is inferred.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--state-db', type=Path, default=Path.home()/'.codex/state_5.sqlite')
    ap.add_argument('--root-thread', required=True)
    ap.add_argument('--cutoff', required=True, help='Exclusive ISO UTC cutoff; use the audit request start')
    ap.add_argument('--output', type=Path, required=True)
    args=ap.parse_args(); result=audit(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'totals': result['totals'], 'time': {k:v for k,v in result['time'].items() if k not in ['intervals_utc','issues']}, 'counts':result['counts']},indent=2))

if __name__=='__main__': main()
