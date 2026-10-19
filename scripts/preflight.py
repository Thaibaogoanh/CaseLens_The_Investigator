#!/usr/bin/env python3
"""Read-only release checks. Does not deploy, publish or call a model."""
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def get_json(url):
    with urllib.request.urlopen(url,timeout=20) as response:
        return json.loads(response.read(1000000))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',help='The deployed HTTPS app URL, or an http://127.0.0.1 local URL.')
    parser.add_argument('--repo',help='Your public https://github.com/owner/repository URL.')
    args=parser.parse_args();checks=[]
    checks.append(dict(check='Python 3.11+',status='pass' if sys.version_info>=(3,11) else 'fail'))
    required=['server.py','Dockerfile','README.md','app/engine.py','app/schema.py','static/index.html','static/extensions.js']
    missing=[name for name in required if not (ROOT/name).is_file()]
    checks.append(dict(check='Required source files',status='fail' if missing else 'pass',detail=missing))
    try:
        proc=subprocess.run(['git','ls-files'],cwd=ROOT,capture_output=True,text=True,check=False)
        if proc.returncode:
            checks.append(dict(check='Git tracking',status='pending',detail='Initialize the repository before checking tracked files.'))
        else:
            tracked=proc.stdout.splitlines()
            sensitive=[name for name in tracked if Path(name).name=='.env' or (Path(name).name.startswith('.env.') and Path(name).name!='.env.example') or name.endswith(('.pem','.key'))]
            checks.append(dict(check='Tracked secret-file names',status='fail' if sensitive else 'pass',detail=sensitive or 'Filename check only; inspect staged contents yourself.'))
    except OSError:
        checks.append(dict(check='Git available',status='pending',detail='Install Git to publish the repository.'))
    if args.url:
        base=args.url.rstrip('/');parsed=urllib.parse.urlsplit(base)
        if parsed.scheme!='https' and not(parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1')):
            parser.error('Use HTTPS for a public app or HTTP for localhost.')
        try:
            health=get_json(base+'/health');config=get_json(base+'/api/config')
            checks.append(dict(check='App health',status='pass' if health.get('status')=='ok' else 'fail'))
            checks.append(dict(check='Server AI key configured',status='pass' if config.get('ai_available') else 'fail',detail='Configuration presence only; does not prove provider access.'))
            checks.append(dict(check='App version',status='pass' if config.get('version')=='2.3.0' else 'fail',detail=config.get('version')))
        except (OSError,ValueError,urllib.error.URLError) as error:
            checks.append(dict(check='App reachable',status='fail',detail=type(error).__name__))
    else:
        checks.append(dict(check='Deployed URL',status='pending',detail='Pass --url after deployment.'))
    if args.repo:
        parsed=urllib.parse.urlsplit(args.repo)
        if parsed.scheme!='https' or parsed.hostname!='github.com' or len(parsed.path.strip('/').split('/'))!=2:
            parser.error('Use a public https://github.com/owner/repository URL.')
        try:
            with urllib.request.urlopen(urllib.request.Request(args.repo,headers={'User-Agent':'CaseLens-release-check'}),timeout=20) as response:
                checks.append(dict(check='Public repo reachable',status='pass' if response.status==200 else 'fail',detail='Reachability only; review source and visibility manually.'))
        except (OSError,urllib.error.URLError):
            checks.append(dict(check='Public repo reachable',status='fail'))
    else:
        checks.append(dict(check='Public repository URL',status='pending',detail='Pass --repo after publishing.'))
    checks.append(dict(check='Live semantic quality and portal submission',status='manual',detail='Run live evals, inspect answers, then verify submitted status in the event portal.'))
    print(json.dumps({'checks':checks,'note':'A successful preflight is not a submitted entry or a live-AI quality certification.'},indent=2))
    return 1 if any(c['status']=='fail' for c in checks) else 0


if __name__=='__main__':sys.exit(main())
