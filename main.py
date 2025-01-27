"""
apt-repo-updater: Update an APT repository based on releases pulled from a Github repository.

Requires PyGithub
"""

from github import Github
import os
import re
import urllib.request
import subprocess
import traceback
from datetime import datetime

GH_PAT_PATH = os.environ['GHPATPATH']

with open(GH_PAT_PATH) as f:
    TOKEN = f.read().strip()

GPG_PASS_PATH = os.environ['GPGPASSPATH']

PREFIX = '/opt/apt/newpkgs/'

ASSETS = {
    'sharkdp/bat': re.compile(r'bat-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'dandavison/delta': re.compile(r'git-delta-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'bootandy/dust': re.compile(r'du-dust_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'sharkdp/fd': re.compile(r'fd-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    # TODO: re-enable once producing deb packages again
    #'jhspetersson/fselect': ,
    'sharkdp/hexyl': re.compile(r'hexyl-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'sharkdp/hyperfine': re.compile(r'hyperfine-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'Peltoche/lsd': re.compile(r'lsd-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'sharkdp/numbat': re.compile(r'numbat-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'sharkdp/pastel': re.compile(r'pastel-musl_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'BurntSushi/ripgrep': re.compile(r'ripgrep_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'watchexec/watchexec': re.compile(r'watchexec-(?P<version>\d+\.\d+\.\d+.*)-(?P<triple>.*)-musl.deb$'),
    'ducaale/xh': re.compile(r'xh_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'ajeetdsouza/zoxide': re.compile(r'zoxide_(?P<version>\d+\.\d+\.\d+.*)_(?P<arch>.*).deb$'),
    'SRv6d/hanko': re.compile(r'hanko-v(?P<version>\d+\.\d+\.\d+.*)-(?P<arch>.*).deb$'),
}

def most_recent_snapshot():
    proc = subprocess.run(['aptly', 'snapshot', 'list', '-raw'], capture_output=True, cwd=PREFIX)
    if proc.returncode != 0:
        raise RuntimeError("couldn't list snapshots?")
    all_snapshots = proc.stdout.decode()
    return all_snapshots.splitlines()[-1].strip()

def package_in_repo(name, snapshot):
    if name.endswith('.deb'):
        name = name[:-4]
    proc = subprocess.run(['aptly', 'snapshot', 'search', snapshot, name], capture_output=True, cwd=PREFIX)
    if proc.returncode != 0:
        return False
    if proc.stdout.decode().strip() == name:
        return True
    else:
        return False

def download_files(repo, asset_pattern):
    latest_release = repo.get_latest_release()
    assets_to_add = []
    for asset in latest_release.get_assets():
        if asset_pattern.match(asset.name):
            # If already downloaded, nothing to do
            snapshot = most_recent_snapshot()
            if package_in_repo(asset.name, snapshot):
                print(f'Skipping {asset.name}, it has already been added to the repo.')
                continue
            assets_to_add.append(PREFIX + asset.name)
            print(f'Downloading {asset.name}')
            try:
                file, _headers = urllib.request.urlretrieve(asset.browser_download_url, filename=PREFIX + asset.name)
                print(file)
            except urllib.request.HTTPError:
                print(f'Failed downloading {asset.name} due to the following exception:\n')
                traceback.print_exc()
    return assets_to_add


def add_to_repo(assets_to_add):
    print(f'Adding {len(assets_to_add)} assets to the repo.')
    for asset in assets_to_add:
        try:
            cmdline = ['aptly', 'repo', 'add', 'rust-tools', asset]
            print(*cmdline)
            proc = subprocess.run(cmdline, capture_output=True, cwd=PREFIX)
        except subprocess.CalledProcessError:
            print(f'Failed to add asset {asset}:\n')
            traceback.print_exc()
        else:
            print(proc.stdout.decode(), proc.stderr.decode(), sep='\n')


def create_snapshot():
    snapshot_name = f'rust-tools-{datetime.strftime(datetime.now(), "%Y/%m/%d-%H:%M:%S")}'
    print(f'Creating snapshot {snapshot_name}')
    try:
        proc = subprocess.run(['aptly', 'snapshot', 'create', snapshot_name, 'from', 'repo', 'rust-tools'], capture_output=True, cwd=PREFIX)
    except subprocess.CalledProcessError:
        print(f'Failed to create snapshot {snapshot_name}')
        traceback.print_exc()
    else:
        print(proc.stdout.decode(), proc.stderr.decode(), sep='\n')
    return snapshot_name

def publish_snapshot(snapshot):
    print(f'Publishing snapshot {snapshot}')
    try:
        proc = subprocess.run(['aptly', 'publish', 'switch', '-batch', f'-passphrase-file={GPG_PASS_PATH}', 'all', snapshot], capture_output=True, cwd=PREFIX)
    except subprocess.CalledProcessError:
        print(f'Failed to publish snapshot {snapshot}')
        traceback.print_exc()
    else:
        print(proc.stdout.decode(), proc.stderr.decode(), sep='\n')

def update_repo(repo, asset_pattern):
    assets_to_add = download_files(repo, asset_pattern)
    add_to_repo(assets_to_add)


def main():
    g = Github(TOKEN)
    for (repo, asset_pattern) in ASSETS.items():
        print(f'Updating {repo}...')
        try:
            update_repo(g.get_repo(repo), asset_pattern)
        except Exception:
            traceback.print_exc()
        print('Done!')
    snapshot = create_snapshot()
    publish_snapshot(snapshot)

if __name__ == '__main__':
    main()
