spm
===

The lightweight Screen Procfile Manager

Using spm you can start/stop connect/kill Procfile defined services easily.
Either one by one or in bulk by using single characters or full argument names.
For example, consider a Procfile like this:

```
caddy: caddy run
rails: bundle exec rails s
nginx: nginx
```

You can then run `spm s` or `spm start` to start all of these in separate screens.
After that you can run a series of other subcommands to manange them.
Most commands can either run for all Procfile-defined services or by service name.
You can for example restart rails with `spm r rails` or restart them all with `spm r`.

# Install

The default pip-method:

```bash
pip3 install --user --upgrade git+https://github.com/WebinarGeek/spm
```

Or alternatively, the "I don't want to install pip"-method:

```bash
curl https://raw.githubusercontent.com/WebinarGeek/spm/master/spm.py -o ~/.local/bin/spm
chmod +x ~/.local/bin/spm
```

And then make sure that `~/.local/bin` is actually in your `$PATH`.

# Usage

The usage documentation is included in the tool when you run it plain or with `-h`:

```
usage: spm [-h] {start,s,restart,r,quit,q,kill,k,connect,c,help,h,list,l,tail,t} ...

The lightweight Screen Procfile Manager

options:
  -h, --help            show this help message and exit

sub-commands:
  All the valid sub-commands to manage services

  {start,s,restart,r,quit,q,kill,k,connect,c,help,h,list,l,tail,t}
    start (s)           Start all or some services
    restart (r)         Restart all or some services
    quit (q)            Quit all or some services
    kill (k)            Kill all or some services
    connect (c)         Connect to the shell of a service
    help (h)            Show this help and exit
    list (l)            Show a list of services with status
    tail (t)            Show the tail of logs from a service
```

# License

The spm tool is created by [Jelmer van Arnhem](https://github.com/Jelmerro) at [WebinarGeek](https://github.com/gebinarGeek)
and may be copied and modified under the terms of the [MIT license](./LICENSE).
