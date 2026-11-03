#!/usr/bin/env python3
"""Isolated receive-pack/proc-receive guard experiment, not a production receiver."""
from pathlib import Path
import json,os,subprocess,tempfile,time
E={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
E.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Receiver Test',GIT_AUTHOR_EMAIL='test@example.invalid',GIT_COMMITTER_NAME='Receiver Test',GIT_COMMITTER_EMAIL='test@example.invalid')
def argv(repo,*a):return ['git','-C',str(repo),'-c','gc.auto=0','-c','pack.threads=1','-c','index.threads=1',*a]
def git(repo,*a,input=None,ok=True):
 r=subprocess.run(argv(repo,*a),input=input,text=True,capture_output=True,env=E)
 if ok and r.returncode:raise RuntimeError(r.stderr)
 return r
HOOK=r"""#!/usr/bin/env python3
import sys,os,json,subprocess,time
from pathlib import Path
control=Path(__CONTROL__)
def readpkt():
 h=sys.stdin.buffer.read(4)
 if len(h)!=4:raise RuntimeError('short pkt header')
 n=int(h,16)
 if n==0:return None
 if n<4:raise RuntimeError('unexpected special packet')
 b=sys.stdin.buffer.read(n-4)
 if len(b)!=n-4:raise RuntimeError('short packet')
 return b
def writepkt(b):sys.stdout.buffer.write(f'{len(b)+4:04x}'.encode()+b);sys.stdout.buffer.flush()
def flush():sys.stdout.buffer.write(b'0000');sys.stdout.buffer.flush()
def git(*a):return subprocess.run(['git',*a],text=True,capture_output=True)
def pause(mode):
 if (control/'mode').read_text().strip()!=mode:return
 (control/'ready').write_text(mode)
 deadline=time.monotonic()+8
 while not (control/'go').exists():
  if time.monotonic()>deadline:raise RuntimeError('controller timeout')
  time.sleep(.01)
# Negotiate only version1, no push-options or atomic extension in this experiment.
while readpkt() is not None:pass
writepkt(b'version=1\n');flush()
cmds=[]
while True:
 packet=readpkt()
 if packet is None:break
 cmds.append(packet.decode().strip().split())
for old,new,ref in cmds:
 reason=None;p=None
 try:
  if len(cmds)!=1:raise RuntimeError('one command only in test')
  channel=ref.split('/')[3];policy='refs/policy/'+channel
  checked=git('cat-file','-e',new+'^{commit}')
  with (control/'observations.jsonl').open('a') as f:f.write(json.dumps({'ref':ref,'incoming_commit_visible':checked.returncode==0,'quarantine_env_present':bool(os.environ.get('GIT_QUARANTINE_PATH'))})+'\n')
  if checked.returncode:raise RuntimeError('incoming commit unavailable')
  p_oid=git('rev-parse','--verify',policy).stdout.strip()
  if git('show','-s','--format=%s',p_oid).stdout.strip()!='OPEN':raise RuntimeError('EPOCH_CLOSED')
  pause('before-prepare')
  p=subprocess.Popen(['git','update-ref','--stdin'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  p.stdin.write(f'start\nverify {policy} {p_oid}\nupdate {ref} {new} {old}\nprepare\n');p.stdin.flush()
  replies=[p.stdout.readline().strip(),p.stdout.readline().strip()]
  if replies!=['start: ok','prepare: ok']:raise RuntimeError('policy-or-writer-CAS-rejected')
  pause('prepared')
  p.stdin.write('commit\n');p.stdin.flush()
  if p.stdout.readline().strip()!='commit: ok':raise RuntimeError('commit-failed')
  p.stdin.close();p.wait(timeout=5)
  if p.returncode:raise RuntimeError('commit-process-failed')
 except Exception as e:reason=str(e)
 finally:
  if p is not None and p.poll() is None:p.kill();p.wait()
 if reason:writepkt(('ng '+ref+' '+reason+'\n').encode())
 else:writepkt(('ok '+ref+'\n').encode())
flush()
"""
def run():
 with tempfile.TemporaryDirectory(prefix='git-proc-receive-test-',dir='/private/tmp') as td:
  base=Path(td);src=base/'src.git';remote=base/'remote.git';control=base/'control';control.mkdir()
  for r in (src,remote):r.mkdir();git(r,'init','--bare','-q')
  tree=git(src,'mktree',input='').stdout.strip()
  def c(msg,*parents):return git(src,'commit-tree',tree,*[a for parent in parents for a in ('-p',parent)],input=msg+'\n').stdout.strip()
  op=c('OPEN');seal_a=c('SEALED',op);open_b=c('OPEN',op);seal_b=c('SEALED',open_b)
  w0=c('writer initial');w1=c('writer publication1',w0);w2=c('writer publication2',w1)
  fixture=c('fixture archive',seal_a,seal_b,w0)
  git(src,'push','-q',remote.as_uri(),f'{fixture}:refs/heads/fixtures')
  a='refs/heads/data/a/writer';b='refs/heads/data/b/writer'
  for ref,oid in [('refs/policy/a',op),('refs/policy/b',op),(a,w0),(b,w0)]:git(remote,'update-ref',ref,oid)
  hook=remote/'hooks/proc-receive';hook.write_text(HOOK.replace('__CONTROL__',repr(str(control))));hook.chmod(0o755)
  git(remote,'config','receive.procReceiveRefs','refs/heads/data/')
  git(remote,'config','core.filesRefLockTimeout','50')
  def startpush(ref,new,mode):
   for name in ('ready','go'):(control/name).unlink(missing_ok=True)
   (control/'mode').write_text(mode)
   return subprocess.Popen(argv(src,'push',remote.as_uri(),f'{new}:{ref}'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=E)
  def ready(p):
   deadline=time.monotonic()+8
   while not (control/'ready').exists():
    if p.poll() is not None:raise RuntimeError('push exited before control point: '+p.communicate()[1])
    if time.monotonic()>deadline:p.kill();raise RuntimeError('hook ready timeout')
    time.sleep(.01)
  p=startpush(a,w1,'prepared');ready(p)
  try:
   blocked=git(remote,'update-ref','refs/policy/a',seal_a,op,ok=False)
   assert blocked.returncode!=0
   independent=git(remote,'update-ref','refs/policy/b',open_b,op,ok=False)
   assert independent.returncode==0
  finally:(control/'go').write_text('go')
  so,se=p.communicate(timeout=8)
  assert p.returncode==0,(so,se)
  assert git(remote,'rev-parse',a).stdout.strip()==w1
  git(remote,'update-ref','refs/policy/a',seal_a,op)
  (control/'mode').write_text('none')
  afterseal=git(src,'push',remote.as_uri(),f'{w2}:{a}',ok=False)
  assert afterseal.returncode!=0 and 'EPOCH_CLOSED' in afterseal.stderr
  assert git(remote,'rev-parse',a).stdout.strip()==w1
  p=startpush(b,w1,'before-prepare');ready(p)
  try:git(remote,'update-ref','refs/policy/b',seal_b,open_b)
  finally:(control/'go').write_text('go')
  so,se=p.communicate(timeout=8)
  assert p.returncode!=0 and 'policy-or-writer-CAS-rejected' in se,(so,se)
  assert git(remote,'rev-parse',b).stdout.strip()==w0
  observations=[json.loads(line) for line in (control/'observations.jsonl').read_text().splitlines()]
  assert len(observations)==3 and all(o['incoming_commit_visible'] for o in observations)
  return {'scope':'Controlled local file-transport receive-pack/proc-receive integration, one data ref per push, files backend, trusted fixture policy changes. Test hook omits authentication, full packet validation, multi-ref/atomic push support, deletion/archive protocol, robust hook error handling, crash/power-loss and host-provider compatibility. Not a production implementation.','git_version':git(src,'--version').stdout.strip(),'prepared_data_transaction_blocks_same_channel_seal':blocked.returncode!=0,'different_channel_policy_updates_while_prepared':independent.returncode==0,'data_push_commits_then_seal_succeeds':True,'post_seal_data_push_rejected_and_ref_unchanged':True,'seal_between_policy_read_and_prepare_rejects_data_CAS_and_preserves_ref':True,'hook_object_observations':observations}
if __name__=='__main__':print(json.dumps(run(),indent=2))
