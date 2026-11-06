"""Offline PR #10 regressions; standard Python + POSIX sh, no HA or root needed.

Run: python3 -I scripts/recovery/tests/test_review_regressions.py
"""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
LOGIN = ROOT / 'scripts/recovery/recover_login.sh'
EVIDENCE = ROOT / 'scripts/recovery/casaray_evidence.sh'
PYTHON = LOGIN.read_text().split("PY=$(cat <<'EOF'\n", 1)[1].split('\nEOF\n)', 1)[0]


def put(root, path, content):
    p = root / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def archive(files):
    inner = io.BytesIO()
    with tarfile.open(fileobj=inner, mode='w') as t:
        for name, content in files.items():
            data = content.encode()
            m = tarfile.TarInfo('data/' + name)
            m.size = len(data)
            t.addfile(m, io.BytesIO(data))
    outer = io.BytesIO()
    with tarfile.open(fileobj=outer, mode='w') as t:
        m = tarfile.TarInfo('homeassistant.tar')
        m.size = len(inner.getvalue())
        t.addfile(m, io.BytesIO(inner.getvalue()))
    return outer.getvalue()


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cfg = Path(self.tmp.name) / 'config'
        self.cfg.mkdir()
        put(self.cfg, '.storage/auth', json.dumps({'data': {
            'users': [{'id': '1', 'is_owner': True}],
            'credentials': [{'user_id': '1', 'auth_provider_type': 'homeassistant',
                             'data': {'username': 'owner'}}]}}))
        put(self.cfg, 'configuration.yaml', 'default_config:\n')
        self.backup = archive({'.storage/auth_provider.homeassistant': json.dumps(
            {'data': {'users': [{'username': 'owner', 'password': 'OLD'}]}}),
            '.storage/person': '{"data": {"persons": []}}'})

    def python(self, mode, data=b''):
        return subprocess.run([sys.executable, '-c', PYTHON], input=data,
                              env={**os.environ, 'MODE': mode, 'RCFG': str(self.cfg)},
                              capture_output=True, timeout=10)

    def prepare(self):
        r = self.python('prepare', self.backup)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_unchanged_prepared_state_accepted(self):
        self.prepare()
        self.assertEqual(self.python('validate').returncode, 0)

    def test_repaired_store_blocks_retained_plan_before_tools_or_writes(self):
        self.prepare()
        store = put(self.cfg, '.storage/auth_provider.homeassistant', 'REPAIRED')
        before = {str(p): p.read_bytes() for p in self.cfg.rglob('*') if p.is_file()}
        bindir = Path(self.tmp.name) / 'bin'
        bindir.mkdir()
        calls = Path(self.tmp.name) / 'calls'
        for name in ('ha', 'docker', 'curl'):
            tool = put(bindir, name, '#!/bin/sh\necho called >> "$CALLS"\nexit 99\n')
            tool.chmod(0o755)
        r = subprocess.run(['sh', str(LOGIN), 'apply'], input='APPLY\n', text=True,
                           capture_output=True, timeout=10, env={**os.environ,
                           'PATH': str(bindir) + ':' + os.environ['PATH'],
                           'CALLS': str(calls), 'RC_HOST_CONFIG': str(self.cfg)})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('apply is disabled', r.stdout)
        self.assertEqual(store.read_text(), 'REPAIRED')
        self.assertFalse(calls.exists())
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.cfg.rglob('*') if p.is_file()})
        self.assertNotEqual(self.python('validate').returncode, 0)

    def test_changed_live_inputs_refused(self):
        for name in ('.storage/auth', 'configuration.yaml', '.storage/person'):
            with self.subTest(name=name):
                self.prepare()
                p = put(self.cfg, name, 'CHANGED')
                self.assertNotEqual(self.python('validate').returncode, 0)
                p.unlink()
                self.setUp_inputs()

    def setUp_inputs(self):
        put(self.cfg, '.storage/auth', json.dumps({'data': {
            'users': [{'id': '1', 'is_owner': True}],
            'credentials': [{'user_id': '1', 'auth_provider_type': 'homeassistant',
                             'data': {'username': 'owner'}}]}}))
        put(self.cfg, 'configuration.yaml', 'default_config:\n')

    def test_changed_stage_plan_and_legacy_manifest_refused(self):
        for name in ('stage/.storage/person', 'plan.txt', 'prepared_state.json'):
            with self.subTest(name=name):
                self.prepare()
                (self.cfg / '_recovery' / name).write_text('CHANGED')
                self.assertNotEqual(self.python('validate').returncode, 0)
        self.prepare()
        (self.cfg / '_recovery/prepared_state.json').unlink()
        self.assertNotEqual(self.python('validate').returncode, 0)

    def test_apply_revalidates_before_side_effects(self):
        self.prepare()
        put(self.cfg, 'configuration.yaml', 'CHANGED')
        bindir = Path(self.tmp.name) / 'bin'
        bindir.mkdir()
        calls = Path(self.tmp.name) / 'calls'
        docker = put(bindir, 'docker', '#!/bin/sh\nexec "$PYTHON_EXE" -c "$8"\n')
        docker.chmod(0o755)
        for name in ('ha', 'curl'):
            tool = put(bindir, name, '#!/bin/sh\necho called >> "$CALLS"\nexit 99\n')
            tool.chmod(0o755)
        r = subprocess.run(['sh', str(LOGIN), 'apply'], input='APPLY\n', text=True,
                           capture_output=True, timeout=10, env={**os.environ,
                           'PATH': str(bindir) + ':' + os.environ['PATH'],
                           'CALLS': str(calls), 'RC_HOST_CONFIG': str(self.cfg),
                           'RCFG': str(self.cfg), 'MODE': 'validate', 'PYTHON_EXE': sys.executable})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('prepared plan failed revalidation', r.stdout)
        self.assertFalse(calls.exists())
        self.assertFalse((self.cfg / '_recovery/placed.txt').exists())

    def test_dangling_password_store_refused(self):
        self.prepare()
        (self.cfg / '.storage/auth_provider.homeassistant').symlink_to('missing')
        self.assertNotEqual(self.python('validate').returncode, 0)
        r = subprocess.run(['sh', str(LOGIN), 'apply'], input='APPLY\n', text=True,
                           capture_output=True, timeout=10,
                           env={**os.environ, 'RC_HOST_CONFIG': str(self.cfg)})
        self.assertIn('apply is disabled', r.stdout)

    def test_resolved_symlink_allowlist(self):
        source = EVIDENCE.read_text()
        # Exercise the actual ALLOW, DENY and rd definitions without the report entrypoint.
        definitions = source[source.index("ALLOW='"):source.index('\nh()')]
        put(self.cfg, 'packages/private.yaml', 'PRIVATE_CANARY')
        put(self.cfg, 'person.yaml', 'ALLOWED_PERSON')
        link = self.cfg / 'people.yaml'
        for target, accepted in [('packages/private.yaml', False), ('person.yaml', True)]:
            with self.subTest(target=target):
                if link.is_symlink(): link.unlink()
                link.symlink_to(target)
                r = subprocess.run(['sh', '-c', 'C=$1; CR=$1\n' + definitions + '\nrd people.yaml',
                                    'sh', str(self.cfg)], capture_output=True, text=True, timeout=10)
                self.assertEqual(r.returncode == 0, accepted)
                self.assertNotIn('PRIVATE_CANARY', r.stdout)
                if accepted: self.assertEqual(r.stdout, 'ALLOWED_PERSON')


if __name__ == '__main__':
    unittest.main(verbosity=2)
