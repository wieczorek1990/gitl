
gitl
====

Git loop inspired by [gitsh](https://github.com/thoughtbot/gitsh).

Features:

* loop
* branch and file completion
* history

Contributions welcome.

Published under MIT License.

## Installation

### make

To install in `/usr/local/` prefix type:

```bash
git clone git@github.com:wieczorek1990/gitl.git && cd gitl/ && sudo make install
```

### snap

To install download [snap](https://snapcraft.io) and type:

```
snap install gitl
```

Currently I'm trying to figure out how to make `.gitconfig` work as normally.

You might want to link your regular `.gitconfig`:

```
ln -fs ~/.gitconfig ~/snap/gitl/current/.gitconfig
```

If you use aliases, you must precede them with `!git` like so:

```
[alias]
    v = !git version
```

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-white.svg)](https://snapcraft.io/gitl)
