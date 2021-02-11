
gitl
====

Git loop inspired by [gitsh](https://github.com/thoughtbot/gitsh).

Features:

* loop
* branch and file completion
* history

Contributions welcome.

## Installation

### make

To install in `/usr/local/` prefix type:

```bash
git clone git@github.com:wieczorek1990/gitl.git && cd gitl/ && sudo make install
```

### snap

To install with [snap](https://snapcraft.io/) type:

```bash
sudo snap install --edge gitl
sudo snap connect gitl:gitconfig snapd
```

Now you can manage git repositories in `~/snap/gitl/current/`.
