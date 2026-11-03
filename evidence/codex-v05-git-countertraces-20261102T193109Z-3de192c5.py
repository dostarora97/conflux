#!/usr/bin/env python3
"""Local Git mechanism countertraces, not a complete gitcomms implementation."""
from pathlib import Path
import json, os, subprocess, tempfile

env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_NO_REPLACE_OBJECTS='1',
 GIT_AUTHOR_NAME='Mechanism Test',GIT_AUTHOR_EMAIL='test@example.invalid',
 GIT_COMMITTER_NAME='Mechanism Test',GIT_COMMITTER_EMAIL='test@example.invalid')
def git(repo,*args,input=None,ok=True):
 r=subprocess.run(['git','-C',str(repo),'-c','gc.auto=0','-c','core.hooksPath=/dev/null',*args],input=input,text=True,capture_output=True,env=env)
 if ok and r.returncode: raise RuntimeError(r.stderr)
 return r

def run():
 with tempfile.TemporaryDirectory(prefix='gitcomms-v05-traces-',dir='/private/tmp') as td:
  base=Path(td); source=base/'source.git'; reader=base/'reader.git'; shallow=base/'shallow.git'
  for repo in (source,reader,shallow):
   repo.mkdir();git(repo,'init','--bare','-q')
  tree=git(source,'mktree',input='').stdout.strip()
  def commit(msg,parent=None):
   args=['commit-tree',tree]+(['-p',parent] if parent else [])
   return git(source,*args,input=msg+'\n').stdout.strip()
  c=commit('C'); t1=commit('T1',c); t2=commit('T2',c)
  ref='refs/heads/writer'; tracking='refs/remotes/peer/writer'; verified='refs/local-state/last-verified/writer'
  url=source.as_uri()
  git(source,'update-ref',ref,t1)
  git(reader,'fetch','-q',url,f'{ref}:{tracking}')
  git(reader,'update-ref',verified,t1)
  prior=git(reader,'rev-parse',tracking).stdout.strip()
  git(source,'update-ref',ref,t2,t1)
  git(reader,'fetch','-q',url,f'+{ref}:{tracking}')
  fetched=git(reader,'rev-parse',tracking).stdout.strip()
  first_check=git(reader,'merge-base','--is-ancestor',prior,fetched,ok=False).returncode
  # Simulate return/restart or crash with only mutable tracking ref retained.
  restarted_prior=git(reader,'rev-parse',tracking).stdout.strip()
  restart_check=git(reader,'merge-base','--is-ancestor',restarted_prior,fetched,ok=False).returncode
  cursor_check=git(reader,'merge-base','--is-ancestor',c,fetched,ok=False).returncode
  retained_check=git(reader,'merge-base','--is-ancestor',verified,fetched,ok=False).returncode
  assert (first_check,restart_check,cursor_check,retained_check)==(1,0,0,1)

  inc='550e8400-e29b-41d4-a716-446655440000'
  cursor=f'refs/gc/cursor/engineering/{inc}'
  git(reader,'update-ref',cursor,c)
  collision=git(reader,'update-ref',cursor+'/consumer-a',c,ok=False)
  assert collision.returncode != 0 and 'exists' in collision.stderr

  git(shallow,'fetch','-q','--depth=1',url,f'{ref}:refs/remotes/peer/writer')
  git(shallow,'fetch','-q','--depth=1',url,c)
  endpoints_present=all(git(shallow,'cat-file','-e',oid+'^{commit}',ok=False).returncode==0 for oid in (c,t2))
  is_shallow=git(shallow,'rev-parse','--is-shallow-repository').stdout.strip()=='true'
  shallow_check=git(shallow,'merge-base','--is-ancestor',c,t2,ok=False).returncode
  complete_check=git(source,'merge-base','--is-ancestor',c,t2,ok=False).returncode
  assert endpoints_present and is_shallow and shallow_check==1 and complete_check==0
  return {'scope':'Deterministic local bare/file Git mechanism tests; does not execute full v0.5 reader or prove production durability.',
    'restart_after_overwritten_tracking':{'initial_prior_tip_rejects_sibling':first_check==1,'after_restart_tracking_self_check_accepts':restart_check==0,'older_cursor_check_accepts':cursor_check==0,'separate_retained_verified_tip_still_rejects':retained_check==1},
    'cursor_namespace':{'existing_default_cursor_prevents_consumer_child_ref':collision.returncode!=0},
    'shallow_ancestry':{'both_endpoint_objects_present':endpoints_present,'repository_shallow':is_shallow,'shallow_is_ancestor_exit':shallow_check,'complete_is_ancestor_exit':complete_check}}
if __name__=='__main__':print(json.dumps(run(),indent=2))
