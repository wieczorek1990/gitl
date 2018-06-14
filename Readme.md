
gitl
====

Git loop inspired by [gitsh](https://github.com/thoughtbot/gitsh).

Features:

* loop
* branch and file completion

Contributions welcome.

Published under MIT License.

## Installation

### make

To install in `/usr/local/` prefix type:

```bash
sudo make install
```

### Snapcraft

To install download [snap](https://snapcraft.io) and type:

```bash
snap install gitl
```

Link your `.gitconfig` to `~/snap/gitl/current/`:

```bash
ln -s $HOME/.gitconfig $HOME/snap/gitl/current/.gitconfig
```

## Snapcraft 101

Debugging snap:

```bash
snapcraft
snap install --classic --dangerous gitl_$version_amd64.snap
snap run --shell gitl
```

Releasing new snap into `stable` channel:

```bash
snapcraft
snapcraft push gitl_$version_amd64.snap
# snap info gitl
snapcraft release gitl $revision stable
snap refresh --amend gitl
```
