#!/usr/bin/env python3
"""Test unchanged policy-ref verification in Git ref transactions, not a receive hook."""
import os,json,subprocess,tempfile
from pathlib import Path
E={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
E.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Policy Test',GIT_AUTHOR_EMAIL='test@example.invalid',GIT_COMMITTER_NAME='Policy Test',GIT_COMMITTER_EMAIL='test@example.invalid')
def args(repo,*a):return ['git','-C',str(repo),'-c','core.hooksPath=/dev/null','-c','gc.auto=0','-c','core.filesRefLockTimeout=50',*a]
def git(repo,*a,input=None,ok=True):
 r=subprocess.run(args(repo,*a),input=input,text=True,capture_output=True,env=E)
 if ok and r.returncode:raise RuntimeError(r.stderr)
 return r

def run():
 with tempfile.TemporaryDirectory(prefix='git-policy-transaction-',dir='/private/tmp') as td:
  repo=Path(td);git(repo,'init','--bare','-q')
  tree=git(repo,'mktree',input='').stdout.strip()
  def c(msg,parent=None):return git(repo,'commit-tree',tree,*(['-p',parent] if parent else []),input=msg+'\n').stdout.strip()
  op=c('epoch OPEN');closed=c('epoch SEALED',op);old=c('writer old');new=c('writer new',old)
  policy='refs/policy/channel-a';other='refs/policy/channel-b';writer='refs/heads/channel-a/writer'
  git(repo,'update-ref',policy,op);git(repo,'update-ref',other,op);git(repo,'update-ref',writer,old)
  proc=subprocess.Popen(args(repo,'update-ref','--stdin'),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=E)
  try:
   proc.stdin.write(f'start\nverify {policy} {op}\nupdate {writer} {new} {old}\nprepare\n');proc.stdin.flush()
   replies=[proc.stdout.readline().strip(),proc.stdout.readline().strip()]
   assert replies==['start: ok','prepare: ok'],replies
   seal_while_prepared=git(repo,'update-ref',policy,closed,op,ok=False)
   assert seal_while_prepared.returncode!=0 and 'lock' in seal_while_prepared.stderr
   independent=git(repo,'update-ref',other,closed,op,ok=False)
   assert independent.returncode==0
   proc.stdin.write('commit\n');proc.stdin.flush()
   commit_reply=proc.stdout.readline().strip();proc.stdin.close();proc.wait(timeout=5)
   assert commit_reply=='commit: ok' and proc.returncode==0
   assert git(repo,'rev-parse',writer).stdout.strip()==new
   assert git(repo,'rev-parse',policy).stdout.strip()==op
  finally:
   if proc.poll() is None:proc.kill();proc.wait()
  git(repo,'update-ref',policy,closed,op)
  late=c('late writer',new)
  stale=git(repo,'update-ref','--stdin',input=f'start\nverify {policy} {op}\nupdate {writer} {late} {new}\nprepare\ncommit\n',ok=False)
  assert stale.returncode!=0
  unchanged=git(repo,'rev-parse',writer).stdout.strip()==new
  assert unchanged
  return {'scope':'Local files ref backend transaction primitive only. No proc-receive integration, object quarantine handling, authentication, crash/power-loss test, throughput or external effects.','git_version':git(repo,'--version').stdout.strip(),'unchanged_policy_verify_blocks_competing_seal_while_prepared':seal_while_prepared.returncode!=0,'different_channel_policy_can_update_concurrently':independent.returncode==0,'data_commits_without_mutating_policy':True,'after_seal_stale_policy_verify_rejects_whole_data_transaction':stale.returncode!=0,'rejected_data_ref_unchanged':unchanged}
if __name__=='__main__':print(json.dumps(run(),indent=2))
