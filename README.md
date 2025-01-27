# Rust Tools apt repo

This is a simple apt repo hosting popular Rust tools which you can access at [apt.cli.rs](https://apt.cli.rs).

The plan is to update the repo when these tools make new releases, so you automatically get the latest and greatest (and don't have to manually install `.deb` files).


### Current packages available

Currently the list is somewhat small, but suggestions are welcome! Feel free to file an issue at https://github.com/emmatyping/apt.cli.rs

- [bat](https://github.com/sharkdp/bat)
- [delta](https://github.com/dandavison/delta)
- [dust](https://github.com/bootandy/dust)
- [fd](https://github.com/sharkdp/fd)
- ~~[fselect](https://github.com/jhspetersson/fselect)~~ (Disabled due to no new deb packages)
- [hanko](https://github.com/SRv6d/hanko)
- [hexyl](https://github.com/sharkdp/hexyl)
- [hyperfine](https://github.com/sharkdp/hyperfine)
- [lsd](https://github.com/Peltoche/lsd)
- [numbat](https://github.com/sharkdp/numbat)
- [pastel](https://github.com/sharkdp/pastel)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [watchexec](https://github.com/watchexec/watchexec)
- [xh](https://github.com/ducaale/xh)
- [zoxide](https://github.com/ajeetdsouza/zoxide)

### How to add the repo

```
$ curl -fsSL https://apt.cli.rs/pubkey.asc | sudo tee -a /usr/share/keyrings/rust-tools.asc
$ curl -fsSL https://apt.cli.rs/rust-tools.list | sudo tee /etc/apt/sources.list.d/rust-tools.list
$ sudo apt update
$ apt show ripgrep
```

### Browsing the apt repo

If you want to find the `Release` or `*.deb` files yourself, they are available here:

[pool](https://apt.cli.rs/pool/)

[dists](https://apt.cli.rs/dists/)

