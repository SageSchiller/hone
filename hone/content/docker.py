"""Docker: images, containers, and the build cache.

Docker earns a module because the mental model genuinely rewires you, and
because it is already load-bearing in this roster: the SMB/AD, Metasploit and
web-discovery modules all tell you to spin up a lab in a container, and this is
where that stops being a magic incantation. The idea to hold is the difference
between an **image** (a read-only template) and a **container** (a running
instance of one), and underneath both, **layers**: an image is a stack of
cached diffs, which is what makes builds fast and pulls small once you
understand it.

The second reframe is what a container is not. It is not a virtual machine. It
shares the host kernel and is really just a process with its filesystem, network
and process table isolated by kernel features. That is why a container starts in
milliseconds and a VM takes a minute, and it is why "it works on my machine"
stops being a sentence: the machine travels with the code.

**Verification.** Docker is not installed on this machine, so the challenges
split honestly per D8. Writing a Dockerfile or a compose file is a file, so
those are verified in the sandbox by reading the file back. Actually running a
container needs the daemon, so those challenges are self-marked and say so. The
drills are the commands themselves, graded as typed text.
"""

MODULE = {
    'id': 'docker',
    'title': 'Docker',
    'group': 'Containers',
    'blurb': 'Images vs containers, layers, the Dockerfile, volumes, ports and compose.',
    'context': 'You are at a shell prompt with the docker command available.',
    'needs': ['docker'],
    'prereqs': ['linux'],
    'adapter': 'sandbox',
    'estimate': '4-5 hours',
    'order': 64,

    'lessons': [
        {
            'id': 'dk-why',
            'title': 'The problem containers solve',
            'next': 'dk-model',
            'concept': (
                'A container is how you ship a program with everything it '
                'depends on, without shipping a second operating system. '
                'That is why the thing you tested is the thing that runs, '
                'on a laptop and on a server.\n\n'
                'The old answer was a **virtual machine**: ship a whole '
                'simulated computer, operating system and all. It works and '
                'it is enormous, gigabytes per copy, a minute to boot, and '
                'you are running a second kernel to host one small '
                'program.\n\n'
                '**A container is the same idea with the heavy part removed.** '
                'It packages the program and everything it depends on, but '
                'shares the host\'s kernel rather than bringing its own. So it '
                'starts in milliseconds, weighs megabytes, and you can run '
                'thirty of them on a laptop.\n\n'
                'What you get is **isolation without simulation**. The process '
                'inside sees its own filesystem, its own network interface '
                'and its own process list, and none of it is emulated: it is '
                'one ordinary Linux process that has been lied to about what '
                'exists. That is why it is fast, and also why a container is '
                'a weaker security boundary than a VM.\n\n'
                'Docker is the tool that builds, runs and ships these. The '
                'payoff is that the thing you tested is the thing that runs, '
                'byte for byte, on your laptop and on the server. Everything '
                'in this module is in service of that one property.'
            ),
            'examples': [
                {
                    'label': 'Three ways to run a program elsewhere',
                    'code': ('on the host    fast, and depends on\n'
                             '               whatever is installed\n'
                             '\n'
                             'in a VM        isolated, whole extra OS,\n'
                             '               gigabytes, slow to start\n'
                             '\n'
                             'in a container isolated, shares the kernel,\n'
                             '               megabytes, instant'),
                    'note': 'The middle option is not obsolete. It is the '
                            'stronger boundary, and you pick it when you are '
                            'isolating something hostile rather than '
                            'something merely fussy.',
                },
                {
                    'label': 'What the container thinks it can see',
                    'code': ('its own /            not yours\n'
                             'its own process 1    not systemd\n'
                             'its own network      its own address\n'
                             '\n'
                             'all of it the host kernel,\n'
                             'answering carefully'),
                    'note': 'Run `ps` inside a container and you see almost '
                            'nothing. That is the isolation, and it is '
                            'bookkeeping rather than simulation.',
                },
                {
                    'label': 'The one-line version of the payoff',
                    'code': ('docker run -it python:3.12 python\n'
                             '\n'
                             'a working Python 3.12, on any machine\n'
                             'with docker, without installing Python'),
                    'note': 'Nothing was added to your system, and nothing '
                            'has to be removed afterwards. That is the whole '
                            'pitch in one command.',
                },
            ],
            'misconceptions': [
                'A container is not a lightweight virtual machine. There is '
                'no second kernel and no emulation; it is a normal process '
                'with a restricted view.',
                'Containers are not primarily a security feature. They are an '
                'isolation and packaging feature, and a VM is the stronger '
                'boundary when the thing inside is hostile.',
                'Docker is not the only container runtime. podman, containerd '
                'and others run the same images, because the image format is '
                'a standard rather than a product.',
            ],
            'try_it': [
                'Run `docker run -it --rm alpine sh`, then `ps` and `ls /` '
                'inside it. Compare with the same commands outside.',
                'Exit that shell and run `ls` on your own machine to confirm '
                'that nothing you did in there touched anything out here.',
            ],
        },
        {
            'id': 'dk-model',
            'title': 'Images, containers, and layers',
            'next': 'dk-run',
            'concept': (
                'Two words carry the whole model and they are not '
                'interchangeable. An **image** is a read-only template: a '
                'snapshot of a filesystem plus a bit of metadata saying what to '
                'run. A **container** is a running, or stopped, instance of an '
                'image, with a thin writable layer added on top. One image can '
                'start a hundred containers, exactly as one program on disk can '
                'become a hundred processes. Most confusion about Docker is '
                'really confusion between these two.\n\n'
                'Underneath, an image is built in **layers**. Each instruction '
                'that builds it adds a layer, which is just the set of files '
                'that changed. Layers are cached and shared: if ten images all '
                'start from the same base, that base is stored once, and if you '
                'rebuild an image after changing one line, only the layers from '
                'that line onward are rebuilt. Understanding layers is what '
                'turns Docker from slow and mysterious into fast and '
                'predictable.\n\n'
                'The reframe that matters most: a container is not a virtual '
                'machine. It does not boot an operating system. It shares the '
                'host kernel and is really just a process whose view of the '
                'filesystem, the network, the process list and the users is '
                'isolated by kernel features called namespaces and cgroups. '
                'That is why a container starts in milliseconds, why it is '
                'small, and why the running thing inside it shows up as an '
                'ordinary process on the host.\n\n'
                'And that is the point of the whole tool: the image bundles the '
                'code with everything it needs to run, so the same image runs '
                'identically on your laptop, a colleague\'s, and a server. "It '
                'works on my machine" stops being an excuse because the machine '
                'now travels with the code.'
            ),
            'examples': [
                {
                    'label': 'One image, many containers',
                    'code': ('image   nginx:latest      read-only template\n'
                             '  |\n'
                             '  +-- container web1      running instance\n'
                             '  +-- container web2      another, same image\n'
                             '  +-- container web3      each with its own\n'
                             '                          writable layer'),
                    'note': 'Image is to container as a program on disk is to a '
                            'running process.',
                },
                {
                    'label': 'A container is a process, not a VM',
                    'code': ('docker run -d nginx        starts in ~0.1s\n'
                             'ps aux | grep nginx        it is a host process\n'
                             '\n'
                             'a VM would boot a kernel and take a minute'),
                    'note': 'Shared kernel, isolated by namespaces and cgroups. '
                            'That is the whole speed difference.',
                },
            ],
            'misconceptions': [
                'An image and a container are not the same thing. The image is '
                'the template; the container is a running instance of it. You '
                'run images and you stop containers.',
                'A container is not a lightweight VM. It shares the host '
                'kernel, which is why it starts instantly and why a Linux '
                'container needs a Linux kernel underneath.',
                'Changing a file inside a running container does not change the '
                'image. It lands in the container\'s writable layer and is '
                'gone when the container is removed.',
            ],
            'try_it': [
                'Run `docker run hello-world`, then `docker ps -a` to see the '
                'container it left behind, then `docker images` to see the '
                'image it pulled.',
            ],
        },
        {
            'id': 'dk-run',
            'title': 'Running containers, and their lifecycle',
            'next': 'dk-images',
            'concept': (
                '`docker run image` creates a container from an image and '
                'starts it. The flags on that command are most of daily Docker, '
                'and they fall into a few groups.\n\n'
                'How it attaches: `-it` gives you an interactive terminal, '
                'which is how you get a shell in a container; `-d` runs it '
                'detached in the background, which is how you run a service; '
                'and `--rm` deletes the container when it exits, which keeps '
                'you from drowning in stopped containers. How it connects: `-p '
                '8080:80` publishes a port, mapping host port 8080 to container '
                'port 80, and the order is host-then-container, which everyone '
                'gets backwards once. How it is configured: `-e KEY=value` sets '
                'an environment variable, `-v` mounts data, and `--name web` '
                'gives it a name you can refer to instead of a random id.\n\n'
                'The lifecycle is separate from run. `docker ps` lists running '
                'containers and `docker ps -a` includes stopped ones. `docker '
                'exec -it web bash` opens a shell in an already-running '
                'container, which is how you look inside one. `docker logs web` '
                'shows what a detached container has printed, which is how you '
                'debug it. `docker stop web` stops it and `docker rm web` '
                'removes it.\n\n'
                'The mental split worth holding: `run` makes a new container '
                'every time, while `start`, `stop` and `exec` act on ones that '
                'already exist. Running `docker run` twice gives you two '
                'containers, not one restarted, which is the surprise behind a '
                'pile of stopped duplicates.\n\n'
                'The image name on that command is still a loose end. The next '
                'lesson is where images come from, and why a missing tag is '
                'already a choice.'
            ),
            'examples': [
                {
                    'label': 'Restarting a container you already made',
                    'code': 'docker start web           start it in the background\ndocker start -ai web       start it and attach to it\n\n-a attaches output, -i keeps stdin open',
                    'note': 'docker run makes a new container every time, which is how people end up with forty of them. start reuses the one you already have.',
                },
                {
                    'label': 'The run flags you reach for',
                    'code': ('docker run -it ubuntu bash      a shell in a '
                             'container\n'
                             'docker run -d --name web -p 8080:80 nginx\n'
                             'docker run --rm alpine echo hi   runs and '
                             'cleans up\n'
                             'docker run -e TOKEN=abc myapp     set an env var'),
                    'note': '-p is host:container. -d for a service, -it for a '
                            'shell, --rm to not leave a mess.',
                },
                {
                    'label': 'Acting on containers that exist',
                    'code': ('docker ps            running containers\n'
                             'docker ps -a         include stopped ones\n'
                             'docker exec -it web bash   shell into a running '
                             'one\n'
                             'docker logs -f web   follow its output\n'
                             'docker stop web && docker rm web'),
                    'note': 'run creates a new container; exec and logs act on '
                            'one already running.',
                },
            ],
            'misconceptions': [
                '`-p 8080:80` is host port first, container port second. '
                'Reversing it publishes the wrong port and nothing answers.',
                '`docker run` twice starts two containers. To restart the same '
                'one use `docker start`, not another run.',
                'A detached container that "does nothing" usually did print '
                'something. `docker logs` shows it; the output did not vanish, '
                'it just was not on your terminal.',
            ],
            'try_it': [
                'Run nginx detached with `-p 8080:80`, open localhost:8080, '
                'then `docker exec -it` into it and look at '
                '`/etc/nginx/nginx.conf`.',
            ],
        },
        {
            'id': 'dk-images',
            'title': 'Images: pulling, listing, and the latest trap',
            'next': 'dk-dockerfile',
            'concept': (
                '`docker pull` is how you download an image from a registry, '
                'and Docker Hub is the default. That is why a `docker run` '
                'line can name nginx on a machine that has never seen it: '
                'run pulls automatically if the image is not local. `docker '
                'images` lists what you have and `docker rmi` removes one.\n\n'
                'An image is named `repository:tag`, and the tag is where a '
                'real trap lives. `nginx:1.27` names a specific version; '
                '`nginx:latest`, or just `nginx` with no tag, means "whatever '
                'is currently tagged latest", which changes over time. Building '
                'on `latest` is how a project that worked last month breaks '
                'today with no change on your side. Pin a real version tag for '
                'anything you depend on, and treat `latest` as "give me '
                'something to experiment with".\n\n'
                'Images are content-addressed underneath: each is identified by '
                'a digest, a hash of its contents, and a tag is just a movable '
                'name pointing at a digest. That is why two tags can be the '
                'same image and why `docker pull` sometimes downloads nothing, '
                'because you already have that digest. `docker tag` adds another '
                'name to an image, which is what you do before pushing it '
                'somewhere.\n\n'
                'Pulling a named image is the easy half. The next lesson is '
                'building your own: a Dockerfile, read top to bottom.'
            ),
            'examples': [
                {
                    'label': 'Getting and managing images',
                    'code': ('docker pull nginx:1.27     a specific version\n'
                             'docker images              what is stored locally\n'
                             'docker rmi nginx:1.27      remove an image\n'
                             'docker tag myapp myrepo/myapp:1.0   name it to '
                             'push'),
                    'note': 'run pulls automatically if the image is missing, '
                            'so an explicit pull is often optional.',
                },
                {
                    'label': 'latest moved, the pinned tag did not',
                    'code': ('docker pull nginx:1.27\n'
                             'docker pull nginx            same as :latest\n'
                             'docker images\n'
                             '\n'
                             'nginx  1.27    a6bd71f\n'
                             'nginx  latest  9c1296e     different image'),
                    'note': 'A Dockerfile that said FROM nginx last month and '
                            'today did not use the same bytes. FROM nginx:1.27 '
                            'cannot drift.',
                },
            ],
            'misconceptions': [
                '`latest` is not "the newest version". It is a tag like any '
                'other that happens to be called latest, and it moves. Pin a '
                'real version for anything you rely on.',
                'No tag means `:latest`. `docker run nginx` and `docker run '
                'nginx:latest` are the same command.',
                'An image name with a slash, like `myrepo/myapp`, names a '
                'registry path. A name with no slash is a Docker Hub official '
                'image.',
            ],
            'try_it': [
                'Pull `alpine:3.19` and `alpine:latest`, run `docker images`, '
                'and note whether they share a digest.',
            ],
        },
        {
            'id': 'dk-dockerfile',
            'title': 'Building an image with a Dockerfile',
            'next': 'dk-data',
            'concept': (
                'A Dockerfile is how you write a recipe for an image, one '
                'instruction and one layer at a time. That is why a rebuild '
                'can reuse every layer that did not change, and take a second '
                'instead of a minute. `FROM` names the base image to start '
                'from. `RUN` executes a command at build time, which is how '
                'you install things. '
                '`COPY` brings files from your project into the image. '
                '`WORKDIR` sets the directory later instructions run in. And '
                'one of `CMD` or `ENTRYPOINT` says what to run when a container '
                'starts.\n\n'
                '`docker build -t myapp .` builds the image from the Dockerfile '
                'in the current directory and tags it `myapp`. The dot is the '
                'build context, the set of files Docker can see, which is why a '
                'huge context directory makes builds slow and why `.dockerignore` '
                'exists.\n\n'
                'The build cache is the thing worth understanding, because it '
                'decides whether a rebuild takes a second or a minute. Docker '
                'caches each layer and reuses it if nothing that layer depends '
                'on has changed. The consequence is an ordering rule: put the '
                'things that change rarely early and the things that change '
                'often late. Copy your dependency manifest and install '
                'dependencies before you copy your source code, so that editing '
                'a source file does not bust the cache on the slow dependency '
                'install. Getting that order right is most of what makes a '
                'Dockerfile good.\n\n'
                'One genuine subtlety: `CMD` gives a default command that '
                '`docker run` can override, while `ENTRYPOINT` sets a command '
                'that always runs, with `CMD` supplying its default arguments. '
                'For a simple app, `CMD` is what you want.\n\n'
                'A **multistage** file has two `FROM` lines. `FROM golang AS '
                'build` compiles. `FROM alpine` then `COPY --from=build '
                '/app /app` keeps the binary and drops the compiler. That '
                'is how a small runtime image is made. `ENV KEY=val` sets '
                'an environment variable in the image; `EXPOSE 8080` '
                'documents a port and does not publish it. `-p` is still '
                'what opens the port on the host.'
            ),
            'examples': [
                {
                    'label': 'A small Dockerfile',
                    'code': ('FROM python:3.12-slim\n'
                             'WORKDIR /app\n'
                             'COPY requirements.txt .\n'
                             'RUN pip install -r requirements.txt\n'
                             'COPY . .\n'
                             'CMD ["python", "app.py"]'),
                    'note': 'requirements are copied and installed BEFORE the '
                            'source, so editing source does not re-run the '
                            'slow install.',
                },
                {
                    'label': 'Building it',
                    'code': ('docker build -t myapp .        build and tag\n'
                             'docker build -t myapp:2.0 .     a version tag\n'
                             'docker run --rm myapp           run what you '
                             'built'),
                    'note': 'The . is the build context. A .dockerignore keeps '
                            'junk out of it and builds fast.',
                },
            ],
            'misconceptions': [
                'Layer order is not cosmetic. Copying source before installing '
                'dependencies means every source edit reruns the install. Copy '
                'the manifest first.',
                'Each `RUN` is its own layer, so `RUN apt-get update` in one '
                'layer and `RUN apt-get install` in the next can use a stale '
                'update. Chain them with `&&` in one RUN.',
                '`CMD` is a default the run command can override; `ENTRYPOINT` '
                'always runs. Using ENTRYPOINT when you meant CMD makes the '
                'container ignore the command you pass it.',
            ],
            'try_it': [
                'Write the Dockerfile above for a one-file script, `docker '
                'build -t mine .`, then `docker run --rm mine`.',
            ],
        },
        {
            'id': 'dk-data',
            'title': 'Data and networking: volumes and ports',
            'next': 'dk-compose',
            'concept': (
                'A container\'s filesystem is disposable. The writable layer is '
                'destroyed when the container is removed, so anything a database '
                'wrote inside a container is gone with it. That is by design, '
                'and **volumes** are how you keep data that should survive.\n\n'
                'There are two shapes. A **named volume**, `-v pgdata:/var/lib/'
                'postgresql/data`, is storage Docker manages, and it outlives '
                'the container, which is right for a database. A **bind mount**, '
                '`-v $(pwd):/app`, maps a directory on your host into the '
                'container, so edits on either side are seen on both, which is '
                'right for developing code you want to change live. The '
                'distinction is worth holding: named volumes for data the '
                'container owns, bind mounts for files you own and want to '
                'share in.\n\n'
                'Networking has two parts you meet early. **Publishing a port** '
                'with `-p 8080:80` is how the outside world reaches a service, and it means the outside world: a published port binds 0.0.0.0 and is reachable from the network, not just from your host. `-p 127.0.0.1:8080:80` is the localhost-only form, and Docker writes its own firewall rules that bypass your INPUT chain '
                'inside a container; without it, the service is only reachable '
                'from other containers, not from your host. **Container '
                'networks** are how containers reach each other: put two '
                'containers on the same user-defined network and they can talk '
                'by container name, because Docker runs a small DNS for them. '
                'That name-based addressing is what makes multi-container setups '
                'work without hardcoding IPs, and it is the foundation the next '
                'lesson builds on.'
            ),
            'examples': [
                {
                    'label': 'Keeping data alive',
                    'code': ('docker run -d -v pgdata:/var/lib/postgresql/data '
                             'postgres\n'
                             '                    named volume: survives the '
                             'container\n'
                             'docker run -v "$(pwd)":/app -w /app node npm test\n'
                             '                    bind mount: your files, live'),
                    'note': 'Named volume for data the container owns; bind '
                            'mount for files you own and edit.',
                },
                {
                    'label': 'Talking to and between containers',
                    'code': ('docker run -d -p 8080:80 --name web nginx\n'
                             '                    reach it at localhost:8080\n'
                             'docker network create appnet\n'
                             'docker run -d --network appnet --name db postgres\n'
                             'docker run --network appnet --name api myapi\n'
                             '                    api reaches the db as "db"'),
                    'note': 'On a shared network, containers reach each other '
                            'by name via Docker\'s built-in DNS.',
                },
            ],
            'misconceptions': [
                'Data written inside a container is not persistent. Remove the '
                'container and it is gone unless it was on a volume.',
                'Without `-p`, a service in a container is not reachable from '
                'your host, even though it is running. Publishing the port is '
                'what exposes it.',
                'Containers on the default bridge cannot resolve each other by '
                'name. Create a user-defined network, and then name-based DNS '
                'works.',
            ],
            'try_it': [
                'Run a container writing to a named volume, remove it, run a '
                'new one on the same volume, and confirm the data is still '
                'there.',
            ],
        },
        {
            'id': 'dk-compose',
            'title': 'Compose: many containers as one file',
            'next': 'dk-hygiene',
            'concept': (
                'Real applications are several containers: a web service, a '
                'database, maybe a cache. Running each with a long `docker run` '
                'command, on the right network, with the right volumes and '
                'ports, and in the right order, is tedious and easy to get '
                'wrong. **Compose** turns that whole thing into one file you '
                'commit alongside the code.\n\n'
                'A `compose.yaml` describes **services**, each of which is a '
                'container: which image or build to use, which ports to '
                'publish, which volumes to mount, which environment to set. '
                'Compose creates a network for them automatically, so they '
                'reach each other by service name with no extra work. `docker '
                'compose up` starts the whole stack and `docker compose down` '
                'stops and removes it, which is why a project with a compose '
                'file is often a single command to run.\n\n'
                '`depends_on` sets start order, though with a caveat worth '
                'knowing: it waits for a container to start, not for the '
                'service inside it to be ready, so a database may be starting '
                'while your app tries to connect. A healthcheck plus '
                '`depends_on: condition: service_healthy` is the honest fix.\n\n'
                'This is also why the security lab modules point you at '
                'compose. A vulnerable-app lab is a `compose.yaml`, `docker '
                'compose up -d`, and you have a target on an isolated network in '
                'one command, torn down as cleanly as it went up.'
            ),
            'examples': [
                {
                    'label': 'A two-service stack',
                    'code': ('services:\n'
                             '  web:\n'
                             '    build: .\n'
                             '    ports:\n'
                             '      - "8080:80"\n'
                             '    depends_on:\n'
                             '      - db\n'
                             '  db:\n'
                             '    image: postgres:16\n'
                             '    volumes:\n'
                             '      - pgdata:/var/lib/postgresql/data\n'
                             'volumes:\n'
                             '  pgdata:'),
                    'note': 'web reaches db as the hostname "db". One file, one '
                            'network, one command to bring it up.',
                },
                {
                    'label': 'Driving the stack',
                    'code': ('docker compose up -d       start it all, '
                             'detached\n'
                             'docker compose ps          what is running\n'
                             'docker compose logs -f web what one service says\n'
                             'docker compose down         stop and remove it '
                             'all'),
                    'note': 'down -v also removes the named volumes, which '
                            'wipes the data. Leave -v off to keep it.',
                },
            ],
            'misconceptions': [
                '`depends_on` waits for the container to start, not for the app '
                'inside to be ready. A database may still be initialising when '
                'your app connects.',
                '`docker compose down` keeps named volumes by default; `down '
                '-v` deletes them. That flag is how you accidentally wipe a '
                'database.',
                'Services reach each other by service name, not by localhost. '
                'Inside the web container, the database is at `db`, not '
                '`127.0.0.1`.',
            ],
            'try_it': [
                'Write the compose file above, `docker compose up -d`, confirm '
                'both containers run with `docker compose ps`, then `down`.',
            ],
        },
        {
            'id': 'dk-hygiene',
            'title': 'Cleanup, debugging, and the security notes',
            'concept': (
                'Docker quietly fills your disk. Every build leaves old layers, '
                'every stopped container lingers, every unused image sits '
                'there. `docker system df` shows how much space each is using, '
                'and `docker system prune` reclaims it: dangling images, '
                'stopped containers and unused networks. Add `-a` and it also '
                'removes images no container is using, which is more aggressive '
                'and worth understanding before you run it.\n\n'
                'Debugging a container comes down to three commands. `docker '
                'logs` shows what it printed, which is the first thing to '
                'check. `docker exec -it container sh` opens a shell inside a '
                'running one so you can look around. And `docker inspect` dumps '
                'everything Docker knows about a container or image as JSON: its '
                'mounts, its network, its environment, the exact command it '
                'runs. When a container exits immediately, `docker logs` on the '
                'stopped container is almost always the answer.\n\n'
                'The security reality is worth stating plainly, because Docker '
                'makes some sharp things easy. By default the process in a '
                'container runs as root, and that root is the host\'s root, so '
                'a container breakout is a serious event; a `USER` line in the '
                'Dockerfile drops to an unprivileged user. Secrets baked into '
                'an image with `ENV` or `COPY` are readable by anyone who pulls '
                'it, layers and all, so credentials belong in runtime '
                'environment or a secrets mechanism, never in the image. And '
                'mounting the Docker socket into a container hands that '
                'container control of the host, which is the single most '
                'over-granted permission in practice.\n\n'
                'None of that is a reason to avoid Docker. It is the reason to '
                'read a Dockerfile before you run the image it built.'
            ),
            'examples': [
                {
                    'label': 'Reclaiming space',
                    'code': ('docker system df          what is using disk\n'
                             'docker system prune       stopped containers, '
                             'dangling images\n'
                             'docker system prune -a    also unused images '
                             '(aggressive)\n'
                             'docker image prune         just dangling images'),
                    'note': 'prune -a can remove an image you meant to keep but '
                            'were not running. Read what it lists first.',
                },
                {
                    'label': 'Debugging, and dropping root',
                    'code': ('docker logs container        what it printed\n'
                             'docker exec -it c sh         look inside a '
                             'running one\n'
                             'docker inspect c             everything, as JSON\n'
                             '\n'
                             'in the Dockerfile:  USER appuser   not root'),
                    'note': 'A container that exits at once: docker logs on the '
                            'stopped container is the answer.',
                },
            ],
            'misconceptions': [
                'A container that "just exits" did not fail silently. `docker '
                'logs` on the stopped container shows why, almost every time.',
                'root in a container is the host\'s root. A `USER` line and not '
                'mounting the Docker socket are the two habits that matter most.',
                'Secrets in an image are not hidden. Every layer is readable by '
                'anyone with the image, so a credential COPYed in is a '
                'credential leaked.',
            ],
            'try_it': [
                'Run `docker system df`, then `docker system prune` and read '
                'exactly what it removed. Then `docker inspect` a container and '
                'find its mounts in the JSON.',
            ],
        },
    ],

    'drills': [
        {'id': 'dkd-run-it', 'type': 'command',
         'answer': 'docker run -it ubuntu bash',
         'prompt': 'Start an interactive shell in a new ubuntu container.',
         'teach': '-it gives an interactive terminal. This is how you get a '
                  'shell inside a fresh container.'},
        {'id': 'dkd-run-d', 'type': 'command',
         'answer': 'docker run -d --name web -p 8080:80 nginx',
         'prompt': 'Run nginx in the background named web, publishing host '
                   '8080 to container 80.',
         'teach': '-d detaches, -p is host:container. Getting the port order '
                  'backwards is the classic mistake.'},
        {'id': 'dkd-run-rm', 'type': 'command',
         'answer': 'docker run --rm alpine echo hi',
         'prompt': 'Run a throwaway alpine container that echoes hi and cleans '
                   'itself up.',
         'teach': '--rm removes the container when it exits, which keeps '
                  'stopped containers from piling up.'},
        {'id': 'dkd-ps', 'type': 'command', 'answer': 'docker ps -a',
         'prompt': 'List all containers, including the stopped ones.',
         'teach': 'Plain docker ps shows only running containers; -a includes '
                  'the stopped ones you forgot about.'},
        {'id': 'dkd-exec', 'type': 'command',
         'answer': 'docker exec -it web bash',
         'prompt': 'Open a shell inside the already-running container web.',
         'teach': 'exec acts on a running container; run would create a new '
                  'one instead.'},
        {'id': 'dkd-logs', 'type': 'command', 'answer': 'docker logs -f web',
         'prompt': 'Follow the output of the container web.',
         'teach': 'A detached container prints to its log, not your terminal. '
                  'This is the first debugging step.'},
        {'id': 'dkd-stop', 'type': 'command', 'answer': 'docker stop web',
         'prompt': 'Stop the running container web.',
         'teach': 'stop is graceful; docker kill is immediate. rm then removes '
                  'the stopped container.'},
        {'id': 'dkd-rm', 'type': 'command', 'answer': 'docker rm web',
         'prompt': 'Remove the stopped container web.',
         'teach': 'rm removes a container; rmi removes an image. They are '
                  'different objects.'},
        {'id': 'dkd-images', 'type': 'command', 'answer': 'docker images',
         'prompt': 'List the images stored locally.',
         'teach': 'An image is repository:tag. rmi removes one you no longer '
                  'need.'},
        {'id': 'dkd-pull', 'type': 'command', 'answer': 'docker pull nginx:1.27',
         'prompt': 'Download a specific version of the nginx image.',
         'teach': 'Pin a real tag rather than latest, which moves over time '
                  'and breaks builds silently.'},
        {'id': 'dkd-rmi', 'type': 'command', 'answer': 'docker rmi nginx:1.27',
         'prompt': 'Remove the nginx 1.27 image from local storage.',
         'teach': 'You cannot remove an image a container still uses; remove '
                  'the container first.'},
        {'id': 'dkd-tag', 'type': 'command',
         'answer': 'docker tag myapp myrepo/myapp:1.0',
         'prompt': 'Give the image myapp a second name ready to push to '
                   'myrepo.',
         'teach': 'A tag is a movable name pointing at an image digest. '
                  'Tagging is what you do before a push.'},
        {'id': 'dkd-build', 'type': 'command', 'answer': 'docker build -t myapp .',
         'prompt': 'Build an image tagged myapp from the Dockerfile in this '
                   'directory.',
         'teach': 'The dot is the build context. A .dockerignore keeps junk '
                  'out of it and keeps builds fast.'},
        {'id': 'dkd-build-ver', 'type': 'command',
         'answer': 'docker build -t myapp:2.0 .',
         'prompt': 'Build the current directory as image myapp with the tag '
                   '2.0.',
         'teach': 'Versioned tags are how you keep a known-good image around '
                  'while building the next one.'},
        {'id': 'dkd-vol-named', 'type': 'command',
         'answer': 'docker run -d -v pgdata:/var/lib/postgresql/data postgres',
         'prompt': 'Run postgres with a named volume pgdata for its data '
                   'directory.',
         'teach': 'A named volume outlives the container, which is right for a '
                  'database whose data must survive.'},
        {'id': 'dkd-vol-bind', 'type': 'command',
         'answer': 'docker run -v "$(pwd)":/app -w /app node npm test',
         'prompt': 'Mount the current directory into /app and run the tests '
                   'there.',
         'teach': 'A bind mount shares your host files live, which is right '
                  'for code you are editing.'},
        {'id': 'dkd-net-create', 'type': 'command',
         'answer': 'docker network create appnet',
         'prompt': 'Create a user-defined network called appnet.',
         'teach': 'On a user-defined network, containers reach each other by '
                  'name via Docker\'s built-in DNS.'},
        {'id': 'dkd-inspect', 'type': 'command', 'answer': 'docker inspect web',
         'prompt': 'Dump everything Docker knows about the container web.',
         'teach': 'inspect returns JSON: mounts, network, environment, the '
                  'exact command. Pipe it to jq.'},
        {'id': 'dkd-compose-up', 'type': 'command',
         'answer': 'docker compose up -d',
         'prompt': 'Start the whole stack described in the compose file, '
                   'detached.',
         'teach': 'Compose creates the network and starts every service. down '
                  'stops and removes them.'},
        {'id': 'dkd-compose-logs', 'type': 'command',
         'answer': 'docker compose logs -f web',
         'prompt': 'Follow the logs of the web service in the compose stack.',
         'teach': 'compose logs reaches a service by its name in the compose '
                  'file, not a container id.'},
        {'id': 'dkd-compose-down', 'type': 'command',
         'answer': 'docker compose down',
         'prompt': 'Stop and remove the whole compose stack, keeping the '
                   'volumes.',
         'teach': 'down keeps named volumes; down -v deletes them, which wipes '
                  'the data.'},
        {'id': 'dkd-prune', 'type': 'command', 'answer': 'docker system prune',
         'prompt': 'Reclaim space from stopped containers and dangling images.',
         'teach': 'Add -a to also remove images no container uses, which is '
                  'more aggressive; read what it lists first.'},
        {'id': 'dkd-df', 'type': 'command', 'answer': 'docker system df',
         'prompt': 'Show how much disk each Docker object type is using.',
         'teach': 'Docker fills disk quietly. This is how you see where the '
                  'space went before pruning.'},
        {'id': 'dkd-run-e', 'type': 'command',
         'answer': 'docker run -e TOKEN=abc123 myapp',
         'prompt': 'Run myapp with the environment variable TOKEN set to '
                   'abc123.',
         'teach': 'Runtime environment is where secrets belong, never baked '
                  'into the image with ENV or COPY.'},
        {'id': 'dkd-cp', 'type': 'command',
         'answer': 'docker cp web:/etc/nginx/nginx.conf ./nginx.conf',
         'prompt': 'Copy a file out of a running container to the host.',
         'teach': 'Works in both directions, and on stopped containers too, which makes it the quick way to inspect or patch one file.'},
        {'id': 'dkd-start', 'type': 'command',
         'answer': 'docker start -ai web',
         'prompt': 'Restart an existing stopped container and attach to it.',
         'teach': 'start reuses the container you already made; run would build a second one from the image and confuse you later.'},
    ],

    'challenges': [
        {
            'id': 'dkc-dockerfile',
            'title': 'Write a Dockerfile the cache will like',
            'goal': 'Order the instructions so that editing source does not '
                    'rerun the slow dependency install. This is most of what '
                    'makes a Dockerfile good.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'app.py': 'print("hello from the container")\n',
                'requirements.txt': 'requests\n'}},
            'solution': {'shell':
                'cat > Dockerfile <<\'EOF\'\n'
                'FROM python:3.12-slim\n'
                'WORKDIR /app\n'
                'COPY requirements.txt .\n'
                'RUN pip install -r requirements.txt\n'
                'COPY . .\n'
                'CMD ["python", "app.py"]\n'
                'EOF'},
            'steps': [
                {'instruction': 'Start from a slim python base and set the '
                                'working directory to /app.',
                 'hint': 'FROM python:3.12-slim then WORKDIR /app'},
                {'instruction': 'Copy requirements.txt and install it BEFORE '
                                'copying the source, so a source edit does not '
                                'bust the install cache.',
                 'hint': 'COPY requirements.txt . then RUN pip install, THEN '
                         'COPY . .'},
                {'instruction': 'Set the default command to run app.py.',
                 'hint': 'CMD ["python", "app.py"]'},
            ],
            'free': 'Produce a Dockerfile that copies and installs '
                    'requirements before copying the source, and runs app.py.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'Dockerfile': ['FROM python:3.12-slim',
                                                 'COPY requirements.txt',
                                                 'RUN pip install',
                                                 'CMD [']}}},
            'fallback': 'self',
        },
        {
            'id': 'dkc-compose',
            'title': 'Describe a two-service stack in compose',
            'goal': 'A web service that depends on a database, on one network, '
                    'with the database data on a named volume.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'Dockerfile': 'FROM nginx\n'}},
            'solution': {'shell':
                'cat > compose.yaml <<\'EOF\'\n'
                'services:\n'
                '  web:\n'
                '    build: .\n'
                '    ports:\n'
                '      - "8080:80"\n'
                '    depends_on:\n'
                '      - db\n'
                '  db:\n'
                '    image: postgres:16\n'
                '    environment:\n'
                '      POSTGRES_PASSWORD: secret\n'
                '    volumes:\n'
                '      - pgdata:/var/lib/postgresql/data\n'
                'volumes:\n'
                '  pgdata:\n'
                'EOF'},
            'steps': [
                {'instruction': 'Define a web service that builds from the '
                                'local Dockerfile and publishes 8080 to 80.',
                 'hint': 'services: web: build: . ports: - "8080:80"'},
                {'instruction': 'Make web depend on a db service using the '
                                'postgres:16 image, and give the db a '
                                'POSTGRES_PASSWORD: the image refuses to start '
                                'without one.',
                 'hint': 'depends_on: - db, then a db service with an '
                         'environment: POSTGRES_PASSWORD entry'},
                {'instruction': 'Give the db a named volume for its data '
                                'directory, and declare that volume at the '
                                'bottom.',
                 'hint': 'volumes: - pgdata:/var/lib/postgresql/data, then a '
                         'top-level volumes: pgdata:'},
            ],
            'free': 'Produce compose.yaml with a web service (build, port '
                    '8080:80, depends_on db) and a db service (postgres:16, '
                    'named volume pgdata).',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'compose.yaml': ['services:', 'web:',
                                                   '8080:80', 'depends_on:',
                                                   'db:', 'postgres:16',
                                                   'pgdata:']}}},
            'fallback': 'self',
        },
        {
            'id': 'dkc-multistage',
            'title': 'Keep the build tools out of the final image',
            'goal': 'A multi-stage Dockerfile builds in one stage and copies '
                    'only the result into a small final image. This is how '
                    'real images stay small.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'main.go': 'package main\nfunc main() { println("hi") }\n'}},
            'solution': {'shell':
                'cat > Dockerfile <<\'EOF\'\n'
                'FROM golang:1.22 AS build\n'
                'WORKDIR /src\n'
                'COPY . .\n'
                'RUN go build -o /app main.go\n'
                '\n'
                'FROM gcr.io/distroless/base-debian12\n'
                'COPY --from=build /app /app\n'
                'ENTRYPOINT ["/app"]\n'
                'EOF'},
            'steps': [
                {'instruction': 'First stage: a full golang image named build '
                                'that compiles the binary.',
                 'hint': 'FROM golang:1.22 AS build ... RUN go build -o /app main.go'},
                {'instruction': 'Second stage: a tiny base image that copies '
                                'only the compiled binary from the build '
                                'stage.',
                 'hint': 'COPY --from=build /app /app'},
                {'instruction': 'Note that the final image has no compiler, '
                                'just the binary, which is smaller and has '
                                'less to attack.'},
            ],
            'free': 'Produce a multi-stage Dockerfile: a build stage that '
                    'compiles, and a small final stage that copies only the '
                    'binary with COPY --from=build.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'Dockerfile': ['AS build',
                                                 'COPY --from=build']}}},
            'fallback': 'self',
        },
        {
            'id': 'dkc-dockerignore',
            'title': 'Keep the build context small',
            'goal': 'A .dockerignore stops secrets and junk being sent into '
                    'the build, which makes builds faster and images safer.',
            'setup': {'kind': 'sandbox', 'shell': 'bash', 'tree': {
                'Dockerfile': 'FROM alpine\nCOPY . /app\n',
                'app.py': 'x\n',
                '.env': 'SECRET=leaked\n'}},
            'solution': {'shell':
                'cat > .dockerignore <<\'EOF\'\n'
                '.git\n'
                '.env\n'
                'node_modules\n'
                '*.log\n'
                'EOF'},
            'steps': [
                {'instruction': 'Create a .dockerignore that excludes .git, '
                                'the .env secrets file, node_modules and log '
                                'files.',
                 'hint': 'one pattern per line, like a .gitignore'},
                {'instruction': 'Note that COPY . /app would otherwise bake '
                                '.env into the image, where anyone who pulls '
                                'it can read it.'},
            ],
            'free': 'Produce a .dockerignore that excludes at least .git, .env '
                    'and node_modules so they never enter the build context.',
            'verify': {'kind': 'sandbox', 'expect': {
                'file_contains': {'.dockerignore': ['.git', '.env',
                                                    'node_modules']}}},
            'fallback': 'self',
        },
        {
            'id': 'dkc-run-real',
            'title': 'Actually run something',
            'goal': 'The sandbox only checked the files you wrote. This needs '
                    'a real Docker daemon, so it is on your own machine.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Run nginx detached with a published port, and '
                                'open it in a browser.',
                 'hint': 'docker run -d -p 8080:80 --name web nginx'},
                {'instruction': 'Exec a shell into it and change the index '
                                'page, then reload the browser.',
                 'hint': 'docker exec -it web bash'},
                {'instruction': 'Remove the container and run a fresh one. '
                                'Note your change is gone: it was in the '
                                'writable layer.'},
                {'instruction': 'Now do it again with a bind mount for the web '
                                'root, change the file on your host, and watch '
                                'it persist.'},
                {'instruction': 'Finally, build an image from your own '
                                'Dockerfile and run it.'},
            ],
            'free': 'On your own machine: run a service with a published port, '
                    'prove the writable layer is ephemeral, make it persist '
                    'with a volume, and build and run your own image.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
        {
            'id': 'dkc-build-lab',
            'title': 'Stand up a lab stack with compose',
            'goal': 'Tie it to the security modules: bring up a multi-service '
                    'lab in one command, on its own network, and tear it down '
                    'cleanly.',
            'setup': {'kind': 'self'},
            'steps': [
                {'instruction': 'Take a vulnerable-app lab that ships a compose '
                                'file (many CTF and training repos do), or '
                                'write a small one yourself.'},
                {'instruction': 'Bring it up detached and confirm every '
                                'service is running.',
                 'hint': 'docker compose up -d; docker compose ps'},
                {'instruction': 'Confirm the services reach each other by name '
                                'and that only the ports you published are '
                                'exposed to your host.'},
                {'instruction': 'Read the logs of one service, exec into '
                                'another, and inspect the network compose '
                                'created.'},
                {'instruction': 'Tear it all down with down, and decide '
                                'whether you want -v to wipe the volumes too.'},
            ],
            'free': 'On your own machine: bring up a multi-service lab with '
                    'compose, verify service-name networking and published '
                    'ports, then tear it down.',
            'verify': {'kind': 'self'},
            'fallback': 'self',
        },
    ],

    'quiz': [
        {'id': 'dkq-image-container', 'type': 'mcq',
         'prompt': 'What is the difference between an image and a container?',
         'answer': 'An image is a read-only template; a container is a running '
                   'instance of one.',
         'distractors': ['They are the same thing with two names.',
                         'An image runs; a container is stored on disk.',
                         'A container is a smaller image.'],
         'teach': 'Image is to container as a program on disk is to a running '
                  'process. One image, many containers.'},
        {'id': 'dkq-not-vm', 'type': 'mcq',
         'prompt': 'Why does a container start in milliseconds where a VM '
                   'takes a minute?',
         'answer': 'A container shares the host kernel; it does not boot an '
                   'operating system.',
         'distractors': ['Containers are compiled to native code.',
                         'Docker keeps every container in memory.',
                         'A VM has to download its disk each time.'],
         'teach': 'A container is an isolated process, not a machine. Namespaces '
                  'and cgroups do the isolating.'},
        {'id': 'dkq-port-order', 'type': 'mcq',
         'prompt': 'In `-p 8080:80`, which number is the host port?',
         'answer': '8080; the format is host:container.',
         'distractors': ['80; the container comes first.',
                         'Neither; both must match.',
                         'It depends on the image.'],
         'teach': 'Host first, container second. Reversing it publishes the '
                  'wrong port and nothing answers.'},
        {'id': 'dkq-latest', 'type': 'mcq',
         'prompt': 'Why is building on `nginx:latest` risky?',
         'answer': 'latest is a moving tag, so the base can change under you '
                   'and break a build that worked before.',
         'distractors': ['latest is always an old version.',
                         'latest images are unofficial.',
                         'latest cannot be pulled without login.'],
         'teach': 'Pin a real version tag for anything you depend on. latest is '
                  'for experimenting.'},
        {'id': 'dkq-cache-order', 'type': 'mcq',
         'prompt': 'Why copy requirements.txt and install before copying the '
                   'source?',
         'answer': 'So editing a source file does not invalidate the cache on '
                   'the slow dependency install.',
         'distractors': ['Because COPY must come before RUN.',
                         'Because the source needs the dependencies at build '
                         'time.',
                         'It makes no difference; Docker reorders it.'],
         'teach': 'Layers cache top to bottom. Put what changes rarely early '
                  'and what changes often late.'},
        {'id': 'dkq-ephemeral', 'type': 'mcq',
         'prompt': 'A database container is removed and its data is gone. Why?',
         'answer': 'The data was in the container\'s writable layer, which is '
                   'destroyed with the container, not on a volume.',
         'distractors': ['Docker encrypts data on removal.',
                         'The image was rebuilt.',
                         'Databases cannot run in containers.'],
         'teach': 'Data that must survive goes on a named volume. The '
                  'container filesystem is disposable by design.'},
        {'id': 'dkq-compose-name', 'type': 'mcq',
         'prompt': 'In a compose stack, how does the web service reach the '
                   'database?',
         'answer': 'By the service name, like `db`, over the network compose '
                   'created.',
         'distractors': ['By localhost, since they share a machine.',
                         'By the database\'s published host port.',
                         'By its container id, which you must look up.'],
         'teach': 'Compose runs DNS for its services, so they reach each other '
                  'by name, not by IP or localhost.'},
        {'id': 'dkq-depends', 'type': 'mcq',
         'prompt': 'What does `depends_on` actually guarantee?',
         'answer': 'That the container has started, not that the service '
                   'inside it is ready.',
         'distractors': ['That the depended-on service is fully ready to '
                         'accept connections.',
                         'That the two services share a volume.',
                         'Nothing; it is only documentation.'],
         'teach': 'A database may still be initialising. A healthcheck with '
                  'service_healthy is the honest wait.'},
        {'id': 'dkq-secrets', 'type': 'mcq',
         'prompt': 'Why is COPYing a secrets file into an image dangerous?',
         'answer': 'Every image layer is readable by anyone with the image, so '
                   'the secret is exposed.',
         'distractors': ['It makes the image too large.',
                         'It only works if the file is encrypted.',
                         'Docker refuses to build with secrets present.'],
         'teach': 'Secrets belong in runtime environment or a secrets '
                  'mechanism, never baked into a layer.'},
        {'id': 'dkq-exit', 'type': 'mcq',
         'prompt': 'A container exits immediately after you run it. What is '
                   'the first thing to check?',
         'answer': '`docker logs` on the stopped container, which shows why it '
                   'exited.',
         'distractors': ['Rebuild the image from scratch.',
                         'Run it again with more memory.',
                         'Delete and reinstall Docker.'],
         'teach': 'The output did not vanish. logs on the stopped container is '
                  'the answer almost every time.'},
    ],
}
