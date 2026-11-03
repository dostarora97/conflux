#!/usr/bin/env python3
"""Reproduce v0.4 read-rule countertraces using isolated local Git repos."""
from pathlib import Path
import json, os, subprocess, tempfile

env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_NO_REPLACE_OBJECTS='1',
           GIT_AUTHOR_NAME='Counterexample',GIT_AUTHOR_EMAIL='test@example.invalid',
           GIT_COMMITTER_NAME='Counterexample',GIT_COMMITTER_EMAIL='test@example.invalid')
def git(repo,*args,input=None,ok=True):
    r=subprocess.run(['git','-C',str(repo),'-c','gc.auto=0','-c','core.hooksPath=/dev/null',*args],input=input,text=True,capture_output=True,env=env)
    if ok and r.returncode:raise RuntimeError(r.stderr)
    return r

def run():
    with tempfile.TemporaryDirectory(prefix='gitcomms-read-trace-',dir='/private/tmp') as t:
        d=Path(t)
        repos=[d/x for x in ['source.git','remote.git','reader.git']]
        for repo in repos:
            repo.mkdir();git(repo,'init','--bare','-q')
        source,remote,reader=repos
        ref='refs/heads/gc/a/author'
        tracking='refs/remotes/peer/gc/a/author'
        url=remote.as_uri()
        tree=git(source,'mktree',input='').stdout.strip()
        def commit(label,parent=None):
            args=['commit-tree',tree]
            if parent:args+=['-p',parent]
            msg=f'{label}\n\nGc-Version: 0.4\nGc-To: room:engineering\nGc-Kind: message\n'
            if parent is None:
                msg='Agent initialized\n\nGc-Version: 0.4\nGc-To: agent:author\nGc-Kind: agent-init\nGc-Incarnation: 550e8400-e29b-41d4-a716-446655440000\n'
            return git(source,*args,input=msg).stdout.strip()
        genesis=commit('genesis')
        git(source,'push','-q',url,f'{genesis}:{ref}')
        git(reader,'fetch','-q','--no-tags',url,f'{ref}:{tracking}')
        tip=genesis;cursor=genesis
        trace=[];recovered=[]
        for n in range(1,7):
            advertised=git(reader,'ls-remote','--refs',url,ref).stdout.split()[0]
            tip=commit(f'publication-{n}',tip)
            git(source,'push','-q',url,f'{tip}:{ref}')
            git(reader,'fetch','-q','--no-tags',url,f'+{ref}:{tracking}')
            fetched=git(reader,'rev-parse',tracking).stdout.strip()
            strict_retries=fetched != advertised
            assert strict_retries
            assert git(reader,'merge-base','--is-ancestor',cursor,fetched,ok=False).returncode==0
            delta=git(reader,'rev-list','--reverse',f'{cursor}..{fetched}').stdout.split()
            recovered+=delta;cursor=fetched
            trace.append({'round':n,'advertisement_is_fetched_tip':False,'fetched_tip_extends_cursor':True,'safe_prefix_messages':len(delta)})
        assert len(recovered)==6
        prior_tip=tip
        rewritten=commit('alternate-child-after-genesis',genesis)
        git(source,'push','--force','-q',url,f'{rewritten}:{ref}')
        advertised=git(reader,'ls-remote','--refs',url,ref).stdout.split()[0]
        git(reader,'fetch','-q','--no-tags',url,f'+{ref}:{tracking}')
        fetched=git(reader,'rev-parse',tracking).stdout.strip()
        assert advertised==fetched
        cursor_pass=git(reader,'merge-base','--is-ancestor',genesis,fetched,ok=False).returncode==0
        prior_pass=git(reader,'merge-base','--is-ancestor',prior_tip,fetched,ok=False).returncode==0
        assert cursor_pass and not prior_pass
        return {'scope':'Deterministic local interleaving of the v0.4 pseudocode conditions; not a complete gitcomms implementation or throughput test.',
                'successful_inventory_fetch_cycles':6,'equality_rule_retries':6,'equality_rule_delivered_messages':0,
                'verified_fetched_prefix_delivered_messages':len(recovered),'trace':trace,
                'rewrite_countertrace':{'new_advertisement_matches_fetch':True,'old_cursor_is_ancestor':cursor_pass,'previously_observed_tip_is_ancestor':prior_pass}}
if __name__=='__main__':print(json.dumps(run(),indent=2))
